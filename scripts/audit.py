#!/usr/bin/env python3
"""Read-only local audit, drift detection, and repository validation.

Safety contract:
  - never installs, removes, updates, or starts agent tooling
  - never executes MCP servers, hooks, plugins, or skill scripts
  - never prints environment variable or credential values
  - scans only allowlisted paths
  - writes only repository reports, sanitized snapshots, and local cache
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tomllib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    print("ERROR: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
CACHE_DIR = ROOT / ".local-state"
CACHE_FILE = CACHE_DIR / "skill-cache.json"
CURRENT = ROOT / "local-state" / "current.yaml"
BASELINE = ROOT / "local-state" / "baseline.yaml"
REPORTS = ROOT / "audit"
POLICY = ROOT / "config" / "drift-policy.yaml"
SEED_BACKLOG = ROOT / "config" / "backlog.yaml"
SCHEMA_VERSION = 1

IGNORED_FILES = {".DS_Store"}
IGNORED_DIRS = {"__pycache__", ".git", "node_modules"}

SECRET_PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("openai-key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("github-pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("slack-token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("bearer-value", re.compile(r"(?i)Bearer\s+(?!(<|YOUR_|COLE_|REDACTED|\$|\{\{))[A-Za-z0-9._~+/=-]{16,}")),
    ("auth-url", re.compile(r"https?://[^/\s:]+:[^@\s/]+@")),
]
SENSITIVE_KEY = re.compile(
    r"(?i)(^|[._-])(api[_-]?key|access[_-]?token|token|secret|password|passwd|credential|"
    r"authorization|auth|cookie|bearer|private[_-]?key)([._-]|$)"
)


# --------------------------------------------------------------------------- #
# Paths and small utilities
# --------------------------------------------------------------------------- #

def norm_path(value: object, home: Path = HOME, repo: Path = ROOT) -> str:
    """Normalize machine paths; never expose a username or removable-volume path."""
    s = str(value)
    if not s:
        return s
    s = s.replace(str(repo), "<repo-root>")
    s = s.replace(str(home), "~")
    s = re.sub(r"^/media/[^/]+/.*$", "<external-volume>/<project>", s)
    s = re.sub(r"^/home/[^/]+/", "~/", s)
    return s


def sanitize_url(url: str) -> tuple[str, bool]:
    """Strip URL userinfo and report whether credentials were present."""
    had = bool(re.search(r"://[^/\s@]+@", url))
    return re.sub(r"(://)[^/\s@]+@", r"\1<REDACTED>@", url), had


def first_line(text: str) -> str:
    return (text or "").strip().splitlines()[0].strip() if (text or "").strip() else ""


def safe_version(command: str, timeout: int = 8) -> tuple[str | None, str | None]:
    exe = shutil.which(command)
    if not exe:
        return None, None
    try:
        proc = subprocess.run(
            [exe, "--version"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        version = first_line(proc.stdout or proc.stderr) or None
        return norm_path(exe), norm_path(version) if version else None
    except (OSError, subprocess.TimeoutExpired):
        return norm_path(exe), None


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonc(path: Path):
    """Tolerant JSONC reader for settings files; does not execute anything."""
    text = path.read_text(encoding="utf-8")
    out = []
    i = 0
    in_str = False
    esc = False
    while i < len(text):
        c = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
        elif c == "/" and nxt == "/":
            while i < len(text) and text[i] != "\n":
                i += 1
        elif c == "/" and nxt == "*":
            i += 2
            while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
        else:
            out.append(c)
            i += 1
    return json.loads("".join(out))


def read_toml(path: Path):
    return tomllib.loads(path.read_text(encoding="utf-8"))


def credential_fields(obj, prefix: str = "") -> list[str]:
    """Return dotted paths of credential-like scalar fields, never their values."""
    found: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if SENSITIVE_KEY.search(str(key)) and not isinstance(value, (dict, list)):
                found.append(path)
            elif isinstance(value, (dict, list)):
                found.extend(credential_fields(value, path))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            found.extend(credential_fields(value, f"{prefix}[{idx}]"))
    return sorted(set(found))


def package_from_command(command) -> tuple[str | None, str | None, str]:
    """Extract executable, package, and pin without echoing arbitrary arguments."""
    parts = [str(p) for p in (command if isinstance(command, list) else [command]) if p]
    if not parts:
        return None, None, ""
    exe = Path(parts[0]).name if parts[0].startswith("/") else parts[0]
    def split_spec(spec: str):
        if spec.startswith("@"):
            idx = spec.rfind("@")
            if idx > 0:
                return spec[:idx], spec[idx + 1:]
            return spec, None
        if "@" in spec:
            return tuple(spec.rsplit("@", 1))
        return spec, None
    pkg = ver = None
    if exe not in {"npx", "bunx", "uvx", "pnpm", "yarn"}:
        return None, None, exe
    for token in parts[1:]:
        if token.startswith("--package="):
            pkg, ver = split_spec(token.split("=", 1)[1])
            break
        if token.startswith("-"):
            continue
        if re.match(r"^@?[A-Za-z0-9][\w.-]*(?:/[\w.-]+)?(?:@[\w.^~-]+)?$", token):
            pkg, ver = split_spec(token)
            break
    if pkg in {"npx", "node", "python", "python3", "sh", "bash"}:
        pkg = None
    if pkg:
        display = f"{exe} {pkg}" + (f"@{ver}" if ver else "")
    else:
        display = exe
    return pkg, ver, display


# --------------------------------------------------------------------------- #
# Skill fingerprinting
# --------------------------------------------------------------------------- #

def metadata_signature(root: Path) -> str:
    h = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
        for name in sorted(filenames):
            if name in IGNORED_FILES:
                continue
            p = Path(dirpath) / name
            rel = p.relative_to(root).as_posix()
            try:
                st = p.lstat()
            except OSError:
                continue
            h.update(f"{rel}\0{st.st_size}\0{st.st_mtime_ns}\0".encode())
    return h.hexdigest()


def fingerprint_skill(path: Path, quick: bool = False, cache: dict | None = None) -> dict:
    if path.is_symlink():
        target = path.resolve(strict=False)
        return {
            "symlink": True,
            "symlink_target": norm_path(target),
            "target_exists": target.exists(),
            "tree_hash": None,
            "file_count": 0,
            "total_size": 0,
            "top_level_skill_md": False,
        }
    if not path.is_dir():
        return {"missing": True}
    key = norm_path(path)
    sig = metadata_signature(path)
    cached = (cache or {}).get(key, {})
    if not quick and cached.get("signature") == sig and cached.get("tree_hash"):
        return {
            "symlink": False,
            "tree_hash": cached["tree_hash"],
            "file_count": cached["file_count"],
            "total_size": cached["total_size"],
            "top_level_skill_md": cached["top_level_skill_md"],
        }
    h = hashlib.sha256()
    file_count = 0
    total_size = 0
    links = 0
    for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
        for name in sorted(filenames):
            if name in IGNORED_FILES:
                continue
            p = Path(dirpath) / name
            rel = p.relative_to(path).as_posix()
            file_count += 1
            try:
                st = p.lstat()
            except OSError:
                continue
            if p.is_symlink():
                links += 1
                h.update(f"{rel}\0link:{norm_path(p.resolve(strict=False))}\0".encode())
                continue
            total_size += st.st_size
            if quick:
                h.update(f"{rel}\0{st.st_size}\0{st.st_mtime_ns}\0".encode())
                continue
            try:
                data = p.read_bytes()
            except OSError:
                continue
            h.update(rel.encode() + b"\0" + data + b"\0")
    tree_hash = h.hexdigest()
    result = {
        "symlink": False,
        "tree_hash": tree_hash,
        "file_count": file_count,
        "total_size": total_size,
        "top_level_skill_md": (path / "SKILL.md").is_file(),
        "links": links,
    }
    if cache is not None and not quick:
        cache[key] = {
            "signature": sig,
            "tree_hash": tree_hash,
            "file_count": file_count,
            "total_size": total_size,
            "top_level_skill_md": result["top_level_skill_md"],
        }
    return result


def load_cache() -> dict:
    try:
        return read_json(CACHE_FILE)
    except (OSError, ValueError):
        return {}


def save_cache(cache: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=1, sort_keys=True) + "\n", encoding="utf-8")


SKILL_STORES = [
    ("~/.agents/skills", Path.home() / ".agents" / "skills", "canonical", False),
    ("~/.claude/skills", Path.home() / ".claude" / "skills", "harness-claude", False),
    ("~/.omp/agent/managed-skills", Path.home() / ".omp" / "agent" / "managed-skills", "omp-managed", True),
    ("~/.codex/skills", Path.home() / ".codex" / "skills", "codex", False),
    ("~/.config/opencode/skills", Path.home() / ".config" / "opencode" / "skills", "opencode", False),
    ("~/.copilot/skills", Path.home() / ".copilot" / "skills", "copilot", False),
    ("~/.gemini/config/skills", Path.home() / ".gemini" / "config" / "skills", "gemini", False),
    ("~/.kiro/skills", Path.home() / ".kiro" / "skills", "kiro", False),
]


def collect_skill_stores(quick: bool, cache: dict) -> list[dict]:
    stores = []
    for label, path, kind, redacted in SKILL_STORES:
        item = {
            "path": label,
            "kind": kind,
            "exists": path.is_dir(),
            "redacted": redacted,
            "entries": [],
        }
        if not path.is_dir():
            stores.append(item)
            continue
        names = sorted(n for n in os.listdir(path) if (path / n).is_dir() or (path / n).is_symlink())
        if kind == "codex":
            names = [n for n in names if n != ".system"]
        if redacted:
            hashes = []
            count = 0
            for name in names:
                # Do not cache redacted managed-skill paths (private names).
                fp = fingerprint_skill(path / name, quick=quick, cache=None)
                if not fp.get("missing"):
                    count += 1
                    if fp.get("tree_hash"):
                        hashes.append(fp["tree_hash"])
            item["count"] = count
            item["aggregate_hash"] = hashlib.sha256("".join(sorted(hashes)).encode()).hexdigest() if hashes else None
            stores.append(item)
            continue
        for name in names:
            fp = fingerprint_skill(path / name, quick=quick, cache=cache)
            if fp.get("missing"):
                continue
            item["entries"].append({"name": name, "path": norm_path(path / name), **fp})
        if kind == "codex":
            system = path / ".system"
            item["system_skills"] = sorted(
                n for n in os.listdir(system) if (system / n / "SKILL.md").is_file()
            ) if system.is_dir() else []
        stores.append(item)
    return stores


# --------------------------------------------------------------------------- #
# MCP, plugin, hook, config collection
# --------------------------------------------------------------------------- #

def mcp_entry(harness: str, name: str, config: Path, data: dict) -> dict:
    command = data.get("command")
    args = data.get("args")
    combined = command if args is None else ([command] if isinstance(command, str) else command) + list(args or [])
    pkg, pin, display = package_from_command(combined or [])
    url = data.get("url") or data.get("serverUrl")
    url, url_auth = sanitize_url(str(url)) if url else (None, False)
    transport = data.get("type") or ("stdio" if command else "http" if url else "unknown")
    enabled = bool(data.get("enabled", True)) and not bool(data.get("disabled", False))
    env_names = sorted((data.get("env") or data.get("environment") or {}).keys())
    return {
        "name": name,
        "harness": harness,
        "config_path": norm_path(config),
        "transport": transport,
        "command_display": display,
        "package": pkg,
        "version_pin": pin,
        "url": url,
        "url_has_credentials": url_auth,
        "enabled": enabled,
        "environment_variables": env_names,
        "dynamic": False,
    }


def collect_mcps() -> list[dict]:
    entries: list[dict] = []

    # OpenCode
    p = HOME / ".config" / "opencode" / "opencode.json"
    if p.is_file():
        try:
            servers = (read_json(p).get("mcp") or {}).get("servers") or {}
        except (OSError, ValueError):
            servers = {}
        for name, value in servers.items():
            if isinstance(value, dict):
                entries.append(mcp_entry("opencode", name, p, value))

    # Claude
    p = HOME / ".claude.json"
    if p.is_file():
        try:
            servers = read_json(p).get("mcpServers") or {}
        except (OSError, ValueError):
            servers = {}
        for name, value in servers.items():
            if isinstance(value, dict):
                entries.append(mcp_entry("claude", name, p, value))

    # Codex
    p = HOME / ".codex" / "config.toml"
    if p.is_file():
        try:
            servers = read_toml(p).get("mcp_servers") or {}
        except (OSError, ValueError):
            servers = {}
        for name, value in servers.items():
            if isinstance(value, dict):
                entries.append(mcp_entry("codex", name, p, value))

    # OMP
    p = HOME / ".omp" / "agent" / "mcp.json"
    if p.is_file():
        try:
            servers = read_json(p).get("mcpServers") or {}
        except (OSError, ValueError):
            servers = {}
        for name, value in servers.items():
            if isinstance(value, dict):
                entries.append(mcp_entry("omp", name, p, value))

    # Zed (JSONC)
    p = HOME / ".config" / "zed" / "settings.json"
    if p.is_file():
        try:
            servers = read_jsonc(p).get("context_servers") or {}
        except (OSError, ValueError, json.JSONDecodeError):
            servers = {}
        for name, value in servers.items():
            if isinstance(value, dict):
                entries.append(mcp_entry("zed", name, p, value))

    # Gemini
    p = HOME / ".gemini" / "config" / "mcp_config.json"
    if p.is_file():
        try:
            servers = read_json(p).get("mcpServers") or {}
        except (OSError, ValueError):
            servers = {}
        for name, value in servers.items():
            if isinstance(value, dict):
                entries.append(mcp_entry("gemini", name, p, value))

    # Kiro
    p = HOME / ".kiro" / "settings" / "mcp.json"
    if p.is_file():
        try:
            servers = read_json(p).get("mcpServers") or {}
        except (OSError, ValueError):
            servers = {}
        for name, value in servers.items():
            if isinstance(value, dict):
                entries.append(mcp_entry("kiro", name, p, value))

    return sorted(entries, key=lambda x: (x["harness"], x["name"]))


def plugin_entries_from_installed(path: Path, harness: str) -> list[dict]:
    out = []
    if not path.is_file():
        return out
    try:
        data = read_json(path)
    except (OSError, ValueError):
        return out
    for name, records in (data.get("plugins") or {}).items():
        record = records[0] if isinstance(records, list) and records else records
        if not isinstance(record, dict):
            continue
        out.append({
            "name": name,
            "harness": harness,
            "version": record.get("version"),
            "scope": record.get("scope"),
            "install_path": norm_path(record.get("installPath", "")),
            "enabled": True,
            "managed_by": "plugin manager",
        })
    return out


def opencode_plugin_version(spec: str) -> str | None:
    base = HOME / ".cache" / "opencode" / "npm"
    if not base.is_dir():
        return None
    base_pkg = spec.rsplit("@", 1)[0] if spec.endswith("@latest") else spec
    pattern = spec if spec.endswith("@latest") else f"{spec}@*"
    for wrapper in base.glob(f"{pattern}/*/package.json"):
        try:
            data = read_json(wrapper)
        except (OSError, ValueError):
            continue
        deps = data.get("dependencies") or {}
        if isinstance(deps, dict) and base_pkg in deps:
            return str(deps[base_pkg])
    return None


def collect_plugins() -> list[dict]:
    entries = []
    entries += plugin_entries_from_installed(
        HOME / ".claude" / "plugins" / "installed_plugins.json", "claude"
    )
    entries += plugin_entries_from_installed(
        HOME / ".omp" / "plugins" / "installed_plugins.json", "omp"
    )
    # Codex
    p = HOME / ".codex" / "config.toml"
    if p.is_file():
        try:
            data = read_toml(p)
        except (OSError, ValueError):
            data = {}
        for name, value in (data.get("plugins") or {}).items():
            entries.append({
                "name": name,
                "harness": "codex",
                "version": None,
                "scope": None,
                "install_path": None,
                "enabled": bool(value.get("enabled", True)) if isinstance(value, dict) else True,
                "managed_by": "plugin manager",
            })
    # OpenCode
    p = HOME / ".config" / "opencode" / "opencode.json"
    if p.is_file():
        try:
            data = read_json(p)
        except (OSError, ValueError):
            data = {}
        for spec in data.get("plugin") or []:
            if isinstance(spec, str):
                entries.append({
                    "name": spec,
                    "harness": "opencode",
                    "version": opencode_plugin_version(spec),
                    "scope": "user",
                    "install_path": "~/.cache/opencode/npm",
                    "enabled": True,
                    "managed_by": "opencode bun resolver",
                    "floating": spec.endswith("@latest") or not opencode_plugin_version(spec),
                })
    # VS Code ChatGPT extension
    ext = HOME / ".vscode" / "extensions"
    if ext.is_dir():
        for d in sorted(ext.glob("openai.chatgpt-*")):
            pkg = d / "package.json"
            if pkg.is_file():
                try:
                    data = read_json(pkg)
                except (OSError, ValueError):
                    continue
                entries.append({
                    "name": data.get("name", "openai.chatgpt"),
                    "harness": "vscode",
                    "version": data.get("version"),
                    "scope": None,
                    "install_path": norm_path(d),
                    "enabled": True,
                    "managed_by": "vscode",
                })
    return sorted(entries, key=lambda x: (x["harness"], x["name"], x.get("version") or ""))


def collect_hooks(quick: bool = False) -> dict:
    files = []
    for base in [HOME / ".claude" / "plugins" / "cache", HOME / ".omp" / "plugins" / "cache"]:
        if not base.is_dir():
            continue
        for p in sorted(base.glob("**/hooks/*.json")):
            try:
                data = read_json(p)
            except (OSError, ValueError):
                continue
            triggers = sorted((data.get("hooks") or {}).keys())
            files.append({
                "path": norm_path(p),
                "owner": p.parent.parent.name,
                "triggers": triggers,
                "exists": True,
                "command_count": sum(len(v) for v in (data.get("hooks") or {}).values() if isinstance(v, list)),
            })
    extensions = []
    ext = HOME / ".omp" / "agent" / "extensions"
    if ext.is_dir():
        for p in sorted(ext.glob("*.ts")):
            extensions.append({"name": p.stem, "path": norm_path(p), "exists": True})
    return {
        "git_hooks_path_set": bool(subprocess.run(
            ["git", "config", "--global", "--get", "core.hooksPath"],
            capture_output=True, text=True, check=False
        ).stdout.strip()),
        "hook_files": files,
        "extensions": extensions,
    }


CONFIG_FILES = [
    "~/.config/opencode/opencode.json",
    "~/.claude/settings.json",
    "~/.codex/config.toml",
    "~/.omp/agent/mcp.json",
    "~/.kiro/settings/mcp.json",
    "~/.oleafly/config.json",
    "~/.config/zed/settings.json",
    "~/.gemini/config/mcp_config.json",
]


def collect_configs() -> list[dict]:
    out = []
    for label in CONFIG_FILES:
        p = Path(os.path.expanduser(label))
        item = {
            "path": label,
            "exists": p.is_file(),
            "symlink": p.is_symlink(),
            "mode": None,
            "credential_fields": [],
        }
        if p.is_file():
            try:
                item["mode"] = oct(p.stat().st_mode & 0o777)[2:].zfill(3)
            except OSError:
                pass
            try:
                if p.suffix == ".toml":
                    data = read_toml(p)
                elif p.suffix == ".json":
                    try:
                        data = read_json(p)
                    except json.JSONDecodeError:
                        data = read_jsonc(p)
                else:
                    data = {}
                item["credential_fields"] = credential_fields(data)
            except (OSError, ValueError):
                pass
        out.append(item)
    return out


def collect_external_dependencies() -> list[dict]:
    out = []
    for label, path, kind, redacted in SKILL_STORES:
        if redacted or not path.is_dir():
            continue
        for entry in sorted(path.iterdir()):
            if entry.is_symlink():
                target = entry.resolve(strict=False)
                out.append({
                    "path": norm_path(entry),
                    "kind": kind,
                    "target": norm_path(target),
                    "target_exists": target.exists(),
                })
    # Codex trusted project paths (names are not exported)
    p = HOME / ".codex" / "config.toml"
    if p.is_file():
        try:
            projects = read_toml(p).get("projects") or {}
        except (OSError, ValueError):
            projects = {}
        for project in projects:
            if str(project).startswith(("/media/", "/mnt/")):
                out.append({
                    "path": "<external-volume>/<project>",
                    "kind": "codex-project-trust",
                    "target": "<external-volume>/<project>",
                    "target_exists": Path(project).is_dir(),
                })
    return out


# --------------------------------------------------------------------------- #
# Collector
# --------------------------------------------------------------------------- #

HARNESSES = [
    "opencode", "claude", "codex", "omp", "freebuff", "zed", "delta",
]


def collect_state(quick: bool = False) -> dict:
    cache = load_cache()
    harnesses = []
    for command in HARNESSES:
        exe, version = safe_version(command)
        harnesses.append({
            "name": command,
            "installed": bool(exe),
            "binary_path": exe,
            "version": version,
        })
    state = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "host": {"os": platform.system(), "arch": platform.machine()},
        "mode": "quick" if quick else "full",
        "harnesses": harnesses,
        "skill_stores": collect_skill_stores(quick, cache),
        "mcps": collect_mcps(),
        "plugins": collect_plugins(),
        "hooks": collect_hooks(quick),
        "configs": collect_configs(),
        "external_dependencies": collect_external_dependencies(),
    }
    if not quick:
        save_cache(cache)
    return state


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )


# --------------------------------------------------------------------------- #
# Drift detection
# --------------------------------------------------------------------------- #

def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_policy() -> dict:
    if not POLICY.is_file():
        return {}
    return load_yaml(POLICY) or {}


def severity_for(kind: str, policy: dict) -> str:
    sev = (policy.get("severity") or {})
    return sev.get(kind.lower(), sev.get(kind, "medium"))


def stable_id(category: str, item: str, kind: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", f"{category}-{item}-{kind}".lower()).strip("-")
    return slug[:120]


def finding(category, kind, severity, item, detail, **extra) -> dict:
    out = {
        "id": stable_id(category, item, kind),
        "category": category,
        "type": kind,
        "severity": severity,
        "item": item,
        "detail": detail,
        "status": "open",
    }
    out.update(extra)
    return out


def compare_named(before: list[dict], after: list[dict], key_fields: list[str], category: str,
                  policy: dict, dynamic_names: set[str]) -> list[dict]:
    findings = []
    def key(item):
        return tuple(str(item.get(k)) for k in key_fields)
    b = {key(i): i for i in before}
    a = {key(i): i for i in after}
    for k in sorted(set(b) - set(a)):
        item = b[k]
        expected = item.get("name") in dynamic_names
        kind = "EXPECTED_DYNAMIC" if expected else "REMOVED"
        findings.append(finding(category, kind, "info" if expected else severity_for("removed", policy),
                                ".".join(k), f"{category} removed", expected_dynamic=expected))
    for k in sorted(set(a) - set(b)):
        item = a[k]
        expected = item.get("name") in dynamic_names
        kind = "EXPECTED_DYNAMIC" if expected else "NEW"
        findings.append(finding(category, kind, "info" if expected else severity_for("new", policy),
                                ".".join(k), f"{category} added", expected_dynamic=expected))
    for k in sorted(set(a) & set(b)):
        old, new = b[k], a[k]
        if "version" in old or "version" in new:
            if old.get("version") != new.get("version"):
                findings.append(finding(category, "VERSION_CHANGED", severity_for("version_changed", policy),
                                        ".".join(k), f"{old.get('version')} -> {new.get('version')}"))
        if "version_pin" in old or "version_pin" in new:
            if old.get("version_pin") != new.get("version_pin"):
                findings.append(finding(category, "VERSION_CHANGED", severity_for("version_changed", policy),
                                        ".".join(k), f"pin {old.get('version_pin')} -> {new.get('version_pin')}"))
        for field in ("binary_path", "install_path", "command_display", "url", "transport", "symlink_target", "target"):
            if field in old or field in new:
                if old.get(field) != new.get(field):
                    findings.append(finding(category, "PATH_CHANGED", severity_for("path_changed", policy),
                                            ".".join(k), f"{field} changed", field=field))
        if "enabled" in old or "enabled" in new:
            if old.get("enabled") != new.get("enabled"):
                findings.append(finding(category, "ENABLED_CHANGED", severity_for("enabled_changed", policy),
                                        ".".join(k), f"enabled {old.get('enabled')} -> {new.get('enabled')}"))
        for field in ("tree_hash", "aggregate_hash", "file_count"):
            if field in old and field in new and old.get(field) != new.get(field):
                findings.append(finding(category, "CONFIG_CHANGED", severity_for("config_changed", policy),
                                        ".".join(k), f"{field} changed", field=field))
                break
    return findings


def compare_skill_stores(before: list[dict], after: list[dict], policy: dict) -> list[dict]:
    findings = []
    bmap = {s["path"]: s for s in before}
    amap = {s["path"]: s for s in after}
    for path in sorted(set(bmap) - set(amap)):
        findings.append(finding("skills", "REMOVED", severity_for("removed", policy), path, "skill store removed"))
    for path in sorted(set(amap) - set(bmap)):
        findings.append(finding("skills", "NEW", severity_for("new", policy), path, "skill store added"))
    for path in sorted(set(amap) & set(bmap)):
        old, new = bmap[path], amap[path]
        if old.get("redacted") or new.get("redacted"):
            for field in ("count", "aggregate_hash"):
                if old.get(field) != new.get(field):
                    findings.append(finding("skills", "CONFIG_CHANGED", severity_for("config_changed", policy),
                                            path, f"redacted store {field} changed", field=field))
            continue
        findings += compare_named(
            old.get("entries", []), new.get("entries", []),
            ["name"], "skills", policy, set()
        )
    return findings


def inventory_mcp_documented() -> tuple[set[str], dict]:
    path = ROOT / "inventory" / "mcps.yaml"
    if not path.is_file():
        return set(), {}
    data = load_yaml(path) or {}
    items = data.get("mcps") or []
    names = set()
    info = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        names.add(item["name"])
        info[item["name"]] = item
    return names, info


def inventory_harnesses() -> dict:
    path = ROOT / "inventory" / "harnesses.yaml"
    if not path.is_file():
        return {}
    return {h.get("name"): h for h in (load_yaml(path) or {}).get("harnesses", []) if isinstance(h, dict)}


def static_findings(current: dict, policy: dict) -> list[dict]:
    """Findings that do not depend on a baseline (policy/security invariants)."""
    findings = []
    for m in current.get("mcps", []):
        if m.get("transport") == "stdio" and m.get("package") and not m.get("version_pin") and m.get("enabled"):
            findings.append(finding("mcp", "UNKNOWN", severity_for("floating_version", policy),
                                    f"{m.get('harness')}:{m.get('name')}", "floating MCP package version"))
    for pl in current.get("plugins", []):
        name = str(pl.get("name", ""))
        if pl.get("floating") or name.endswith("@latest"):
            findings.append(finding("plugin", "UNKNOWN", severity_for("floating_version", policy),
                                    f"{pl.get('harness')}:{name}", "floating plugin version"))
    for cfg in current.get("configs", []):
        if cfg.get("credential_fields") and cfg.get("mode") not in {"600", None}:
            findings.append(finding("security", "CONFIG_CHANGED", severity_for("credential_mode", policy),
                                    cfg.get("path", "config"), f"credential-bearing config mode {cfg.get('mode')}"))
    for dep in current.get("external_dependencies", []):
        if not dep.get("target_exists"):
            findings.append(finding("external-dependency", "BROKEN_REFERENCE",
                                    severity_for("broken_reference", policy),
                                    dep.get("path", "external"), "external target missing"))
    return findings


def detect_drift(baseline: dict, current: dict, policy: dict) -> list[dict]:
    findings = []
    dynamic = {e.get("item") for e in policy.get("expected_dynamic", []) if isinstance(e, dict)}
    findings += compare_named(
        baseline.get("harnesses", []), current.get("harnesses", []),
        ["name"], "harness", policy, set()
    )
    findings += compare_skill_stores(baseline.get("skill_stores", []), current.get("skill_stores", []), policy)
    findings += compare_named(
        baseline.get("mcps", []), current.get("mcps", []),
        ["harness", "name"], "mcp", policy, dynamic
    )
    findings += compare_named(
        baseline.get("plugins", []), current.get("plugins", []),
        ["harness", "name"], "plugin", policy, set()
    )
    # Hooks: compare by owner/path/trigger
    def hook_keys(state):
        return {
            (h.get("owner"), h.get("path"), trigger): h
            for h in state.get("hooks", {}).get("hook_files", [])
            for trigger in (h.get("triggers") or ["<none>"])
        }
    bh, ch = hook_keys(baseline), hook_keys(current)
    for key in sorted(set(bh) - set(ch)):
        findings.append(finding("hook", "REMOVED", severity_for("removed", policy), "|".join(key), "hook removed"))
    for key in sorted(set(ch) - set(bh)):
        findings.append(finding("hook", "NEW", severity_for("new", policy), "|".join(key), "hook added"))
    # External dependencies
    findings += compare_named(
        baseline.get("external_dependencies", []), current.get("external_dependencies", []),
        ["path", "kind"], "external-dependency", policy, set()
    )
    # Documented inventory vs current
    documented, _ = inventory_mcp_documented()
    current_mcps = {m["name"] for m in current.get("mcps", [])}
    for name in sorted(documented - current_mcps):
        info = (load_yaml(ROOT / "inventory" / "mcps.yaml") or {}).get("mcps", [])
        entry = next((x for x in info if x.get("name") == name), {})
        if entry.get("source_type") == "plugin-injected" or entry.get("dynamic"):
            continue
        if entry.get("repair_class") in {"Unknown upstream"}:
            continue
        findings.append(finding("mcp", "BROKEN_REFERENCE", severity_for("broken_reference", policy),
                                name, "documented MCP is absent from all current configs"))
    inv_h = inventory_harnesses()
    current_h = {h["name"]: h for h in current.get("harnesses", [])}
    for name, item in inv_h.items():
        if item.get("status") == "Installed" and name in current_h and not current_h[name].get("installed"):
            findings.append(finding("harness", "BROKEN_REFERENCE", severity_for("broken_reference", policy),
                                    name, "documented harness has no executable"))
    findings += static_findings(current, policy)
    return findings


def actionable(findings: list[dict], policy: dict) -> bool:
    exit_on = set(policy.get("exit_on") or ["high", "critical"])
    return any(f.get("severity") in exit_on for f in findings)


# --------------------------------------------------------------------------- #
# Repository validation
# --------------------------------------------------------------------------- #

def iter_text_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", ".local-state", "__pycache__"}]
        for name in filenames:
            p = Path(dirpath) / name
            try:
                if p.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".gz", ".woff", ".woff2", ".ico"}:
                continue
            yield p


def validate_inventory_structure() -> list[str]:
    errors = []
    files = {
        "skills": "entries",
        "mcps": "mcps",
        "harnesses": "harnesses",
        "plugins": "plugins",
        "hooks": "hooks",
    }
    for stem, key in files.items():
        p = ROOT / "inventory" / f"{stem}.yaml"
        if not p.is_file():
            errors.append(f"{p}: missing")
            continue
        try:
            data = load_yaml(p)
        except Exception as exc:
            errors.append(f"{p}: parse error {type(exc).__name__}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{p}: top level is not a mapping")
            continue
        items = data.get(key)
        if not isinstance(items, list):
            errors.append(f"{p}: missing list '{key}'")
            continue
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{p}: item {idx} is not a mapping")
                continue
            if not item.get("name"):
                errors.append(f"{p}: item {idx} lacks name")
            if stem in {"mcps", "harnesses", "plugins"}:
                cat = item.get("category")
                if cat is not None and not isinstance(cat, str):
                    errors.append(f"{p}: item {idx} category is not a string")
    return errors


def _type_ok(value, expected) -> bool:
    mapping = {
        "object": dict, "array": list, "string": str, "boolean": bool,
        "integer": int, "number": (int, float), "null": type(None),
    }
    if isinstance(expected, list):
        return any(_type_ok(value, e) for e in expected)
    if expected == "integer" and isinstance(value, bool):
        return False
    if expected == "number" and isinstance(value, bool):
        return False
    return isinstance(value, mapping.get(expected, object))


def _mini_validate(value, schema, root, path="$") -> list[str]:
    """Small draft-2020 subset validator; no third-party dependency."""
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return []
        target = root
        for part in ref[2:].split("/"):
            target = target.get(part, {})
        return _mini_validate(value, target, root, path)
    errors = []
    expected = schema.get("type")
    if expected and not _type_ok(value, expected):
        return [f"{path}: expected {expected}"]
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing {key}")
        props = schema.get("properties", {})
        for key, sub in props.items():
            if key in value:
                errors.extend(_mini_validate(value[key], sub, root, f"{path}.{key}"))
    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for idx, item in enumerate(value):
            errors.extend(_mini_validate(item, schema["items"], root, f"{path}[{idx}]"))
    return errors


def validate_against_schemas() -> list[str]:
    errors = []
    inv_schema = read_json(ROOT / "schemas" / "inventory.schema.json")
    snap_schema = read_json(ROOT / "schemas" / "snapshot.schema.json")
    for p in sorted((ROOT / "inventory").glob("*.yaml")):
        try:
            errors += [f"{p.relative_to(ROOT)}: {e}" for e in _mini_validate(load_yaml(p), inv_schema, inv_schema)]
        except Exception as exc:
            errors.append(f"{p.relative_to(ROOT)}: schema {type(exc).__name__}")
    for p in [BASELINE, CURRENT]:
        if p.is_file():
            try:
                errors += [f"{p.relative_to(ROOT)}: {e}" for e in _mini_validate(load_yaml(p), snap_schema, snap_schema)]
            except Exception as exc:
                errors.append(f"{p.relative_to(ROOT)}: schema {type(exc).__name__}")
    return errors


def duplicate_inventory_ids() -> list[str]:
    errors = []
    for stem, key in [("harnesses", "harnesses"), ("mcps", "mcps"), ("plugins", "plugins"), ("hooks", "hooks")]:
        p = ROOT / "inventory" / f"{stem}.yaml"
        if not p.is_file():
            continue
        items = (load_yaml(p) or {}).get(key) or []
        names = [i.get("name") for i in items if isinstance(i, dict) and i.get("name")]
        for name, count in duplicate_names(names):
            errors.append(f"{p}: duplicate name '{name}' ({count})")
    # Skills: duplicates are expected across stores; flag duplicate source+path only.
    p = ROOT / "inventory" / "skills.yaml"
    if p.is_file():
        items = (load_yaml(p) or {}).get("entries") or []
        keys = []
        for item in items:
            if not isinstance(item, dict):
                continue
            keys.append((item.get("name"), item.get("source_type"), tuple(item.get("local_paths") or [])))
        for key, count in Counter(keys).items():
            if count > 1:
                errors.append(f"{p}: duplicate skill record '{key[0]}'")
    return errors


def validate_links() -> list[str]:
    errors = []
    for p in iter_text_files(ROOT):
        if p.suffix.lower() != ".md":
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            rel = target.split("#")[0]
            if not rel:
                continue
            full = (p.parent / rel).resolve()
            if not full.exists():
                errors.append(f"{p.relative_to(ROOT)}: broken relative link '{target}'")
    return errors


def secret_categories(line: str) -> list[str]:
    """Return detector names for a line; the caller must not print the line."""
    found = []
    for category, pattern in SECRET_PATTERNS:
        if pattern.search(line):
            found.append(category)
    if re.search(r"(?i)\b(password|secret|token)\b\s*[:=]\s*['\"][^'\"<]{12,}", line):
        found.append("inline-credential")
    return found


def absolute_home_paths(text: str) -> list[int]:
    pattern = re.compile(r"/home/(?!<user>|<username>|[A-Za-z0-9._-]+>)[A-Za-z0-9._-]+/")
    return [idx for idx, line in enumerate(text.splitlines(), 1) if pattern.search(line)]


def duplicate_names(values: list[str]) -> list[tuple[str, int]]:
    return [(name, count) for name, count in Counter(values).items() if count > 1]


def scan_secrets() -> list[str]:
    findings = []
    for p in iter_text_files(ROOT):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for category in secret_categories(line):
                findings.append(f"{p.relative_to(ROOT)}:{lineno}: {category} [REDACTED]")
    return findings


def scan_absolute_paths() -> list[str]:
    findings = []
    for p in iter_text_files(ROOT):
        if p.suffix.lower() not in {".md", ".yaml", ".yml", ".json", ".toml", ".sh", ".py", ".example"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno in absolute_home_paths(text):
            findings.append(f"{p.relative_to(ROOT)}:{lineno}: absolute-home-path")
    return findings


def scan_private_terms() -> list[str]:
    terms_file = ROOT / ".local-state" / "private-terms.txt"
    if not terms_file.is_file():
        return []
    terms = [t.strip() for t in terms_file.read_text(encoding="utf-8").splitlines() if t.strip()]
    if not terms:
        return []
    findings = []
    for p in iter_text_files(ROOT):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if any(term.lower() in line.lower() for term in terms):
                findings.append(f"{p.relative_to(ROOT)}:{lineno}: private-term [REDACTED]")
    return findings


def validate_syntax() -> list[str]:
    errors = []
    for p in sorted((ROOT / "inventory").glob("*.yaml")):
        try:
            load_yaml(p)
        except Exception as exc:
            errors.append(f"{p.relative_to(ROOT)}: YAML {type(exc).__name__}")
    for p in sorted((ROOT / "configs" / "examples").glob("*")):
        try:
            if p.suffix == ".json":
                read_json(p)
            elif p.suffix == ".toml":
                read_toml(p)
        except Exception as exc:
            errors.append(f"{p.relative_to(ROOT)}: {type(exc).__name__}")
    for p in sorted((ROOT / "config").glob("*.yaml")):
        try:
            load_yaml(p)
        except Exception as exc:
            errors.append(f"{p.relative_to(ROOT)}: YAML {type(exc).__name__}")
    for p in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        try:
            load_yaml(p)
        except Exception as exc:
            errors.append(f"{p.relative_to(ROOT)}: YAML {type(exc).__name__}")
    for p in sorted((ROOT / "schemas").glob("*.json")):
        try:
            read_json(p)
        except Exception as exc:
            errors.append(f"{p.relative_to(ROOT)}: JSON {type(exc).__name__}")
    for p in sorted((ROOT / "scripts").glob("*.sh")):
        proc = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True, check=False)
        if proc.returncode:
            errors.append(f"{p.relative_to(ROOT)}: bash syntax error")
    return errors


def validate_freshness(policy: dict) -> list[str]:
    warnings = []
    max_days = int(policy.get("freshness_days") or 90)
    now = datetime.now(timezone.utc).date()
    for p in sorted((ROOT / "inventory").glob("*.yaml")):
        data = load_yaml(p) or {}
        candidates = data.get("entries") or data.get("mcps") or data.get("harnesses") or data.get("plugins") or []
        for item in candidates[:2000]:
            if not isinstance(item, dict):
                continue
            value = item.get("last_verified")
            if not value:
                continue
            try:
                then = datetime.fromisoformat(str(value)).date()
            except ValueError:
                continue
            if (now - then).days > max_days:
                warnings.append(f"{p.relative_to(ROOT)}: '{item.get('name')}' last_verified {value} (> {max_days}d)")
                break
    return warnings


def verify_repository() -> tuple[list[str], list[str]]:
    policy = load_policy()
    errors = []
    errors += validate_inventory_structure()
    errors += validate_against_schemas()
    errors += duplicate_inventory_ids()
    errors += validate_links()
    errors += validate_syntax()
    secrets = scan_secrets()
    abs_paths = scan_absolute_paths()
    private = scan_private_terms()
    errors += secrets + abs_paths + private
    warnings = validate_freshness(policy)
    return errors, warnings


# --------------------------------------------------------------------------- #
# Reports
# --------------------------------------------------------------------------- #

def write_reports(findings: list[dict], current: dict, policy: dict) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    # YAML
    write_yaml(REPORTS / "drift-report.yaml", {
        "schema_version": SCHEMA_VERSION,
        "baseline": "local-state/baseline.yaml",
        "current": "local-state/current.yaml",
        "summary": dict(Counter(f["severity"] for f in findings)),
        "findings": findings,
    })
    # Markdown
    groups = {
        "Critical": [f for f in findings if f["severity"] == "critical"],
        "High": [f for f in findings if f["severity"] == "high"],
        "Medium": [f for f in findings if f["severity"] == "medium"],
        "Low": [f for f in findings if f["severity"] == "low"],
        "Info / expected dynamic": [f for f in findings if f["severity"] == "info"],
    }
    lines = [
        "# Drift report",
        "",
        f"- Baseline: `local-state/baseline.yaml`",
        f"- Current: `local-state/current.yaml`",
        f"- Findings: {len(findings)}",
        "",
        "| Severity | Count |",
        "| --- | ---: |",
    ]
    for name, items in groups.items():
        lines.append(f"| {name} | {len(items)} |")
    lines += ["", "## Changes", ""]
    if not findings:
        lines.append("No drift detected.")
    for name, items in groups.items():
        if not items:
            continue
        lines += [f"### {name}", "", "| Type | Item | Detail |", "| --- | --- | --- |"]
        for f in items:
            detail = str(f.get("detail", "")).replace("|", "\\|")
            lines.append(f"| {f['type']} | `{f['item']}` | {detail} |")
        lines.append("")
    lines += [
        "## Recommended actions",
        "",
        "- Review `High` and `Critical` findings before acting.",
        "- Do not auto-update or auto-remove anything.",
        "- Update the baseline only after reviewing changes: `./scripts/audit.sh --accept-baseline --yes`.",
        "",
        "## Limitations",
        "",
        "- Runtime MCP handshakes, hook execution, and plugin behaviour are not tested.",
        "- Plugin-injected tools are only observed statically; `EXPECTED_DYNAMIC` policy covers known cases.",
        "- Quick mode does not hash skill contents.",
    ]
    (REPORTS / "drift-report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_backlog(findings: list[dict]) -> None:
    seeds = []
    if SEED_BACKLOG.is_file():
        seeds = (load_yaml(SEED_BACKLOG) or {}).get("items") or []
    items = []
    for seed in seeds:
        if isinstance(seed, dict) and seed.get("status", "open") == "open":
            items.append(seed)
    for f in findings:
        if f["severity"] in {"critical", "high", "medium"}:
            items.append({"title": f"{f['type']}: {f['item']}", "severity": f["severity"],
                          "status": "open", "source": "drift", "detail": f.get("detail", "")})
    groups = {"High": [], "Medium": [], "Low": []}
    for item in items:
        sev = str(item.get("severity", "low")).capitalize()
        groups.setdefault(sev, []).append(item)
    lines = ["# Backlog", "", "Unresolved items requiring human judgment. No automatic remediation.", ""]
    for group in ("High", "Medium", "Low"):
        lines += [f"## {group}", ""]
        if not groups.get(group):
            lines.append("_None._")
        for item in groups[group]:
            lines.append(f"- [ ] **{item.get('title')}** — {item.get('detail', '')}".rstrip())
            if item.get("source"):
                lines[-1] += f" (`{item['source']}`)"
        lines.append("")
    (REPORTS / "backlog.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_update_suggestions(check: bool) -> None:
    lines = ["# Update suggestions", "", "Read-only proposals. Nothing is applied automatically.", ""]
    if not check:
        lines += ["Upstream version check was not run. Use `--check-upstreams` to query public registries.", ""]
    else:
        # Only public registry metadata; no credentials and no local data.
        import urllib.request
        packages = [
            ("npm", "mcp-insomnia", "0.8.2"),
            ("npm", "@floriscornel/teams-mcp", "1.0.1"),
            ("npm", "codebase-memory-mcp", "0.12.1"),
            ("npm", "hostinger-api-mcp", "3.8.1"),
            ("pypi", "claude-agent-sdk", "0.2.174"),
        ]
        for kind, name, local in packages:
            try:
                if kind == "npm":
                    with urllib.request.urlopen(f"https://registry.npmjs.org/{name}/latest", timeout=10) as r:
                        upstream = json.load(r).get("version")
                else:
                    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=10) as r:
                        upstream = json.load(r)["info"]["version"]
            except Exception:
                lines.append(f"- `{name}`: upstream check failed (offline or unavailable).")
                continue
            if upstream and upstream != local:
                lines.append(f"- `{name}`: **Available update** {local} → {upstream}. Not recommended automatically.")
            else:
                lines.append(f"- `{name}`: no newer public release found (local {local}).")
    lines += ["", "## Policy", "", "- Available update ≠ recommended update.",
              "- Review changelogs, licenses, and hooks before changing anything.", ""]
    (REPORTS / "update-suggestions.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def cmd_collect(args) -> int:
    state = collect_state(quick=args.quick)
    write_yaml(Path(args.output).resolve() if args.output else CURRENT, state)
    print(f"collected: {norm_path(Path(args.output).resolve() if args.output else CURRENT)} ({state['mode']})")
    return 0


def cmd_verify(args) -> int:
    errors, warnings = verify_repository()
    for w in warnings:
        print(f"WARN {w}")
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        print(f"\nverify: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"\nverify: OK ({len(warnings)} warning(s))")
    return 0


def cmd_drift(args) -> int:
    if not BASELINE.is_file():
        print("ERROR: no baseline. Run `./scripts/audit.sh --full --accept-baseline --yes` first.", file=sys.stderr)
        return 3
    if not CURRENT.is_file():
        print("ERROR: no current snapshot. Run `./scripts/audit.sh --full` first.", file=sys.stderr)
        return 3
    policy = load_policy()
    findings = detect_drift(load_yaml(BASELINE), load_yaml(CURRENT), policy)
    write_reports(findings, load_yaml(CURRENT), policy)
    write_backlog(findings)
    print(f"drift: {len(findings)} finding(s); report: audit/drift-report.md")
    for f in findings:
        if f["severity"] in {"critical", "high"}:
            print(f"  {f['severity'].upper():8} {f['type']}: {f['item']}")
    return 2 if actionable(findings, policy) else 0


def cmd_full(args) -> int:
    rc = cmd_verify(args)
    if rc != 0:
        return rc
    state = collect_state(quick=False)
    write_yaml(CURRENT, state)
    print("collected: local-state/current.yaml (full)")
    if not BASELINE.is_file():
        print("NOTE: no baseline yet. Run `--accept-baseline --yes` after review.")
        return 2
    policy = load_policy()
    findings = detect_drift(load_yaml(BASELINE), load_yaml(CURRENT), policy)
    write_reports(findings, state, policy)
    write_backlog(findings)
    write_update_suggestions(args.check_upstreams)
    print(f"drift: {len(findings)} finding(s); report: audit/drift-report.md")
    for f in findings:
        if f["severity"] in {"critical", "high"}:
            print(f"  {f['severity'].upper():8} {f['type']}: {f['item']}")
    return 2 if actionable(findings, policy) else 0


def cmd_quick(args) -> int:
    rc = cmd_verify(args)
    if rc != 0:
        return rc
    state = collect_state(quick=True)
    write_yaml(CURRENT, state)
    print("collected: local-state/current.yaml (quick)")
    if not BASELINE.is_file():
        print("NOTE: no baseline yet. Run `--full --accept-baseline --yes` after review.")
        return 2
    policy = load_policy()
    findings = detect_drift(load_yaml(BASELINE), state, policy)
    # Quick mode cannot see content hashes; drop hash-only findings.
    findings = [f for f in findings if f.get("field") not in {"tree_hash", "aggregate_hash"}]
    write_reports(findings, state, policy)
    write_backlog(findings)
    print(f"drift: {len(findings)} finding(s)")
    return 2 if actionable(findings, policy) else 0


def cmd_accept_baseline(args) -> int:
    if not args.yes:
        print("Refusing to overwrite baseline without --yes.", file=sys.stderr)
        return 3
    errors, warnings = verify_repository()
    if errors:
        print("Refusing: repository validation failed.", file=sys.stderr)
        return 1
    state = collect_state(quick=False)
    write_yaml(CURRENT, state)
    write_yaml(BASELINE, state)
    print("baseline updated: local-state/baseline.yaml")
    for w in warnings:
        print(f"WARN {w}")
    return 0


def cmd_report_only(args) -> int:
    if not BASELINE.is_file() or not CURRENT.is_file():
        print("ERROR: baseline and current snapshots are required.", file=sys.stderr)
        return 3
    policy = load_policy()
    current = load_yaml(CURRENT)
    findings = detect_drift(load_yaml(BASELINE), current, policy)
    write_reports(findings, current, policy)
    write_backlog(findings)
    print("reports regenerated")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only agent-toolbox audit")
    parser.add_argument("command", nargs="?", default="full",
                        choices=["full", "quick", "verify", "drift", "collect", "report-only", "accept-baseline"])
    parser.add_argument("--quick", action="store_true", help="skip full skill hashing")
    parser.add_argument("--full", action="store_true", help="full local audit (default)")
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--accept-baseline", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--check-upstreams", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    if args.report_only:
        return cmd_report_only(args)
    if args.accept_baseline:
        return cmd_accept_baseline(args)
    if args.quick:
        return cmd_quick(args)
    return {
        "full": cmd_full,
        "quick": cmd_quick,
        "verify": cmd_verify,
        "drift": cmd_drift,
        "collect": cmd_collect,
        "report-only": cmd_report_only,
        "accept-baseline": cmd_accept_baseline,
    }[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
