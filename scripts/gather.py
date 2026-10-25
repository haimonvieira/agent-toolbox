#!/usr/bin/env python3
"""
gather.py — Coleta o estado real do ambiente para dentro de data/.

Lê:
  • /var/minis/skills/*/SKILL.md   → data/skills.json  (as skills instaladas)
  • minis-mcp-cli list/info        → data/mcps.json    (os servidores MCP)

Separado do build.py de propósito: gather.py toca o sistema, build.py só
transforma dados em documentos. Assim o build roda offline e é reprodutível.

Uso:
  python3 scripts/gather.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SKILLS_ROOT = Path("/var/minis/skills")


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm_text = parts[1]
    fm, block_key, block, nested_key, nested = {}, None, [], None, {}

    def flush_block():
        nonlocal block_key, block
        if block_key:
            fm[block_key] = " ".join(block).strip()
        block_key, block = None, []

    def flush_nested():
        nonlocal nested_key, nested
        if nested_key:
            fm[nested_key] = dict(nested)
        nested_key, nested = None, {}

    for raw in fm_text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if not line.startswith((" ", "\t")) and ":" in line:
            flush_block(); flush_nested()
            k, _, v = line.partition(":")
            k, v = k.strip(), v.strip()
            if v in (">", "|", ">-", "|-"):
                block_key, block = k, []
            elif v == "":
                nested_key, nested = k, {}
            else:
                fm[k] = v.strip('"').strip("'")
        else:
            if block_key:
                block.append(line.strip())
            elif nested_key and ":" in line:
                nk, _, nv = line.partition(":")
                nested[nk.strip()] = nv.strip().strip('"').strip("'")
    flush_block(); flush_nested()
    return fm


def gather_skills():
    skills = []
    for d in sorted(SKILLS_ROOT.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        sm = d / "SKILL.md"
        if not sm.exists():
            continue
        txt = sm.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(txt)
        body = txt.split("---", 2)[2] if txt.count("---") >= 2 else ""

        subs = {s: (d / s).is_dir() and any((d / s).iterdir())
                for s in ("scripts", "references", "assets", "evals", "tests", "data")}

        skills.append({
            "dir": d.name,
            "name": fm.get("name") or d.name,
            "description": re.sub(r"\s+", " ", fm.get("description", "")).strip(),
            "version": (fm.get("metadata") or {}).get("version") if isinstance(fm.get("metadata"), dict) else fm.get("version"),
            "license_field": fm.get("license"),
            "has": {k: v for k, v in subs.items() if v},
            "body_lines": len(body.splitlines()),
            "skill_md_bytes": sm.stat().st_size,
            "files": sum(1 for _ in d.rglob("*") if _.is_file()),
        })
    return skills


def gather_mcps():
    out = subprocess.run(["minis-mcp-cli", "list", "--all"],
                         capture_output=True, text=True, timeout=60)
    try:
        d = json.loads(out.stdout)
    except json.JSONDecodeError:
        print("AVISO: não consegui listar os MCPs", file=sys.stderr)
        return []

    servers = d if isinstance(d, list) else d.get("servers", [])
    mcps = []
    for s in servers:
        name = s.get("name")
        info = subprocess.run(["minis-mcp-cli", "info", name],
                              capture_output=True, text=True, timeout=60)
        cfg = {}
        try:
            cfg = json.loads(info.stdout).get("config", {})
        except json.JSONDecodeError:
            pass

        is_http = bool(cfg.get("url"))
        mcps.append({
            "name": name,
            "transport": "http" if is_http else "stdio",
            "url": cfg.get("url"),
            "command": cfg.get("command"),
            "args": cfg.get("args") or [],
            "env_vars": sorted((cfg.get("env") or {}).keys()),
            "header_names": sorted((cfg.get("headers") or {}).keys()),
            "enabled": bool(cfg.get("enabled")),
            "note": cfg.get("note") or s.get("note"),
        })
    return mcps


def main():
    DATA.mkdir(exist_ok=True)
    skills = gather_skills()
    (DATA / "skills.json").write_text(json.dumps(skills, indent=2, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
    print(f"data/skills.json — {len(skills)} skills")

    mcps = gather_mcps()
    (DATA / "mcps.json").write_text(json.dumps(mcps, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
    print(f"data/mcps.json   — {len(mcps)} servidores MCP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
