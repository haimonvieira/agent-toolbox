#!/usr/bin/env python3
"""Versioned environment profiles over the existing agent-toolbox inventory.

Profiles are declarative: they describe an expected environment and reference
inventory entries by stable id. They never install, remove, or execute anything.

Stable id convention
--------------------
``<category>-<slug(name)>`` where category is one of harness|plugin|mcp|skill|hook
and ``slug`` lowercases the name and replaces every run of non-alphanumeric
characters with a single ``-``. Collisions get a deterministic suffix derived
from the inventory record (for example ``-plugin``, ``-harness-bundled``).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

CATEGORIES = ("harness", "plugin", "mcp", "skill", "hook")
PROFILE_KEYS = {
    "harness": "harnesses",
    "plugin": "plugins",
    "mcp": "mcps",
    "skill": "skills",
    "hook": "hooks",
}
STATUSES = ("draft", "active", "deprecated", "archived")
MAX_INHERITANCE_DEPTH = 2

# deterministic ordering: the canonical copy of a skill gets the plain id
SKILL_SOURCE_ORDER = {
    "skills-cli": 0,
    "manual-or-unknown": 0,
    "project-local-symlink": 0,
    "plugin": 1,
    "harness-bundled": 2,
    "omp-managed-local": 3,
    "companion-app": 4,
}

# skill id suffixes for the non-canonical copies of the same skill name
SKILL_VARIANT_SUFFIX = {
    "skills-cli": "canonical",
    "manual-or-unknown": "canonical",
    "project-local-symlink": "canonical",
    "plugin": "plugin",
    "harness-bundled": "built-in",
    "omp-managed-local": "managed",
    "companion-app": "companion",
}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def component_id(category: str, name: str) -> str:
    return f"{category}-{slug(name)}"


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else None


class Catalog:
    """Read-only index over inventory/*.yaml. The only source of component truth."""

    def __init__(self, root: Path):
        self.root = root
        self.entries: dict[str, dict] = {}
        self.by_name: dict[tuple[str, str], list[str]] = {}
        self._load()

    # -- loading ---------------------------------------------------------- #
    def _add(self, category: str, name: str, entry: dict, suffix: str | None = None) -> str:
        base = component_id(category, name)
        cid = base if suffix is None else f"{base}-{suffix}"
        i = 2
        while cid in self.entries:
            cid = f"{base}-{suffix or 'copy'}-{i}"
            i += 1
        record = {
            "id": cid,
            "category": category,
            "name": name,
            "entry": entry,
            "source_type": entry.get("source_type"),
            "evidence_level": entry.get("evidence_level"),
            "version": entry.get("version"),
            "license": entry.get("license"),
            "upstream_repository": entry.get("upstream_repository"),
            "official_docs": entry.get("official_docs"),
            "install_method": entry.get("install_method"),
            "status": entry.get("status"),
            "scope": entry.get("scope"),
            "harnesses": entry.get("harnesses"),
        }
        self.entries[cid] = record
        self.by_name.setdefault((category, name), []).append(cid)
        return cid

    def _load(self) -> None:
        inv = self.root / "inventory"
        mapping = {
            "harnesses": ("harnesses", "harness", None),
            "plugins": ("plugins", "plugin", None),
            "mcps": ("mcps", "mcp", None),
            "hooks": ("hooks", "hook", None),
        }
        for stem, (key, category, _) in mapping.items():
            data = _load_yaml(inv / f"{stem}.yaml") or {}
            for entry in data.get(key) or []:
                if not isinstance(entry, dict) or not entry.get("name"):
                    continue
                self._add(category, entry["name"], entry)
        skills = (_load_yaml(inv / "skills.yaml") or {}).get("entries") or []
        seen: dict[str, int] = {}
        for entry in sorted(
            (e for e in skills if isinstance(e, dict) and e.get("name")),
            key=lambda e: (
                e.get("name"),
                SKILL_SOURCE_ORDER.get(str(e.get("source_type")), 9),
                str(e.get("status")),
            ),
        ):
            name = entry["name"]
            source_type = str(entry.get("source_type"))
            count = seen.get(name, 0)
            seen[name] = count + 1
            if count == 0:
                self._add("skill", name, entry)
            else:
                suffix = SKILL_VARIANT_SUFFIX.get(source_type, slug(source_type))
                if count > 1:
                    suffix = f"{suffix}-{count}"
                self._add("skill", name, entry, suffix=suffix)

    # -- queries ---------------------------------------------------------- #
    def get(self, ref: str) -> dict | None:
        return self.entries.get(ref)

    def find(self, category: str, name: str, variant: str | None = None) -> dict | None:
        ids = self.by_name.get((category, name), [])
        if not ids:
            return None
        if variant is None:
            return self.entries[ids[0]]
        for cid in ids:
            record = self.entries[cid]
            source = SKILL_VARIANT_SUFFIX.get(str(record.get("source_type")), "")
            if source == variant:
                return record
        return self.entries[ids[0]]


# --------------------------------------------------------------------------- #
# Profiles
# --------------------------------------------------------------------------- #

class ProfileError(Exception):
    pass


def load_profiles(root: Path) -> tuple[dict[str, dict], list[str]]:
    """Load profiles/*.yaml and return (profiles, errors)."""
    profiles: dict[str, dict] = {}
    errors: list[str] = []
    directory = root / "profiles"
    if not directory.is_dir():
        return {}, ["profiles/ directory is missing"]
    for path in sorted(directory.glob("*.yaml")):
        data = _load_yaml(path)
        if not isinstance(data, dict):
            errors.append(f"{path.name}: not a mapping")
            continue
        pid = data.get("id")
        if not pid:
            errors.append(f"{path.name}: missing id")
            continue
        if pid in profiles:
            errors.append(f"{path.name}: duplicate profile id '{pid}'")
            continue
        data["_path"] = path.name
        profiles[pid] = data
    errors += inheritance_errors(profiles)
    return profiles, errors


def inheritance_errors(profiles: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    for pid, profile in profiles.items():
        seen = [pid]
        depth = 0
        current = profile
        while current.get("extends"):
            depth += 1
            if depth > MAX_INHERITANCE_DEPTH:
                errors.append(f"{pid}: inheritance depth exceeds {MAX_INHERITANCE_DEPTH}")
                break
            parent_id = current["extends"]
            parents = parent_id if isinstance(parent_id, list) else [parent_id]
            for parent in parents:
                if parent in seen:
                    errors.append(f"{pid}: inheritance cycle via '{parent}'")
                    continue
                seen.append(parent)
                if parent not in profiles:
                    errors.append(f"{pid}: unknown parent profile '{parent}'")
                    continue
                current = profiles[parent]
    return errors


def profile_parents(profile: dict) -> list[str]:
    parent = profile.get("extends")
    if not parent:
        return []
    return parent if isinstance(parent, list) else [parent]


def resolved_components(profile: dict, profiles: dict[str, dict]) -> dict[str, list[dict]]:
    """Merge parent + own components per category, marking inherited ownership."""
    merged: dict[str, list[dict]] = {c: [] for c in CATEGORIES}
    for parent_id in profile_parents(profile):
        parent = profiles.get(parent_id)
        if not parent:
            continue
        for category, items in resolved_components(parent, profiles).items():
            for item in items:
                merged[category].append({**item, "ownership": item.get("ownership", "inherited")})
    for category in CATEGORIES:
        block = profile.get(PROFILE_KEYS[category]) or profile.get(category)
        if not isinstance(block, dict):
            continue
        for requirement, items in block.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict) or not item.get("ref"):
                    continue
                entry = dict(item)
                entry.setdefault("requirement", requirement)
                merged[category].append(entry)
    return merged


def profile_refs(profile: dict, profiles: dict[str, dict]) -> dict[str, list[str]]:
    resolved = resolved_components(profile, profiles)
    return {c: [i["ref"] for i in items] for c, items in resolved.items() if items}


def unresolved_refs(profile: dict, profiles: dict[str, dict], catalog: Catalog) -> list[str]:
    missing = []
    for items in resolved_components(profile, profiles).values():
        for item in items:
            ref = item.get("ref")
            if ref and catalog.get(ref) is None:
                missing.append(ref)
    return sorted(set(missing))


# --------------------------------------------------------------------------- #
# Reproducibility
# --------------------------------------------------------------------------- #

URLISH = re.compile(r"^https?://")


def _reference(record: dict) -> str | None:
    """Best available upstream reference for a component."""
    for field in ("upstream_repository", "official_docs"):
        value = record.get(field)
        if value and URLISH.match(str(value)):
            return str(value)
    entry = record.get("entry") or {}
    for field in ("source", "package_source", "official_docs"):
        value = entry.get(field)
        if value and URLISH.match(str(value)):
            return str(value)
    return None


def _component_facts(record: dict, snapshot: dict | None) -> dict:
    entry = record.get("entry") or {}
    reference = _reference(record)
    install_known = bool(record.get("install_method")) or bool(entry.get("install_method"))
    if not install_known and record.get("category") == "mcp":
        install_known = bool(entry.get("command")) or bool(entry.get("package_source"))
    if not install_known and record.get("category") == "plugin":
        install_known = bool(entry.get("install_method")) or bool(entry.get("update_method"))
    if not install_known and record.get("category") == "harness":
        install_known = bool(entry.get("install_method")) or bool(entry.get("update_method"))
    facts = {
        "reference": reference,
        "verified_upstream": str(record.get("evidence_level", "")) == "Verified upstream",
        "license_known": bool(record.get("license"))
        and "unknown" not in str(record.get("license")).lower(),
        "install_method_known": install_known,
        "pinned_version": bool(record.get("version")),
    }
    if record.get("category") == "mcp":
        facts["executable_present"] = _mcp_executable_present(record)
    if record.get("category") == "skill":
        facts["provenance_known"] = record.get("provenance") not in {"unknown", None}
    return facts


def _mcp_executable_present(record: dict) -> bool | None:
    entry = record.get("entry") or {}
    command = entry.get("command")
    if isinstance(command, list) and command:
        exe = str(command[0])
        if exe.startswith("/") or exe.startswith("~"):
            return Path(os.path.expanduser(exe)).exists()
        return None
    if isinstance(command, str):
        if command.startswith("/") or command.startswith("~"):
            return Path(os.path.expanduser(command)).exists()
        return None
    return None


def compute_reproducibility(profile: dict, profiles: dict[str, dict], catalog: Catalog) -> dict:
    """Score a profile. Conservative: never claims full reproducibility."""
    resolved = resolved_components(profile, profiles)
    reasons: list[str] = []
    minor: list[str] = []
    blockers: list[str] = []
    floating: list[str] = []
    unresolved = profile.get("unresolved") or []
    if isinstance(unresolved, list) and unresolved:
        reasons.append(f"{len(unresolved)} component(s) excluded as unresolved")
    for category, items in resolved.items():
        for item in items:
            if item.get("requirement", "required") != "required":
                continue
            ref = item["ref"]
            record = catalog.get(ref)
            if record is None:
                blockers.append(f"unknown reference '{ref}'")
                continue
            facts = _component_facts(record, None)
            if category in {"harness", "plugin", "mcp"}:
                if not facts["reference"]:
                    blockers.append(f"{ref}: no upstream reference recorded")
                else:
                    if not facts["verified_upstream"]:
                        minor.append(f"{ref}: upstream not verified")
                    if not facts["install_method_known"]:
                        minor.append(f"{ref}: install method not documented")
                if category == "mcp" and facts.get("executable_present") is False:
                    blockers.append(f"{ref}: configured executable is missing")
                if category == "plugin" and record.get("source_type") == "npm-plugin":
                    minor.append(f"{ref}: version resolved by the plugin manager")
            if category == "skill":
                if not facts.get("provenance_known"):
                    reasons.append(f"{ref}: provenance unknown")
                if not facts.get("install_method_known"):
                    minor.append(f"{ref}: install method not documented")
    for item in profile.get("floating_versions") or []:
        floating.append(str(item))
    if floating:
        minor.append(f"{len(floating)} floating version(s)")
    all_reasons = reasons + minor
    if blockers:
        status = "blocked"
    elif not all_reasons:
        status = "fully_reproducible"
    elif not reasons:
        status = "mostly_reproducible"
    else:
        status = "partially_reproducible"
    return {
        "status": status,
        "reasons": all_reasons,
        "blockers": blockers,
        "floating_versions": floating,
    }


# --------------------------------------------------------------------------- #
# Evaluation against a local snapshot
# --------------------------------------------------------------------------- #

def versions_match(expected, actual) -> bool:
    """Compare versions loosely: 'opencode v2.1.4' and '2.1.4' are the same."""
    if expected is None or actual is None:
        return True
    exp = str(expected).strip().lower().lstrip("v")
    act = str(actual).strip().lower().lstrip("v")
    if exp == act:
        return True
    tokens = [t.lstrip("v") for t in re.split(r"[\s/@]+", act) if t]
    return exp in tokens or act.endswith("@" + exp) or act.endswith("-" + exp)


def _profile_harness_names(profile: dict, catalog: Catalog) -> list[str]:
    names = []
    for item in (profile.get("harnesses") or {}).get("required", []) or []:
        record = catalog.get(item.get("ref", ""))
        if record is None:
            continue
        command = (record.get("entry") or {}).get("command")
        if command:
            names.append(str(command))
        names.append(str(record.get("name")))
    return names


def _snapshot_harness(snapshot: dict, record: dict) -> dict | None:
    command = (record.get("entry") or {}).get("command")
    for harness in snapshot.get("harnesses", []):
        if command and harness.get("name") == command:
            return harness
        if slug(harness.get("name", "")) == slug(str(record.get("name"))):
            return harness
    return None


def _snapshot_plugin(snapshot: dict, record: dict) -> dict | None:
    target = slug(record.get("name"))
    for plugin in snapshot.get("plugins", []):
        name = slug(str(plugin.get("name", "")).split("@")[0])
        if name == target:
            return plugin
    return None


def _snapshot_mcp(snapshot: dict, record: dict, harness_names: list[str] | None = None,
                  expected_version=None) -> dict | None:
    matches = [mcp for mcp in snapshot.get("mcps", []) if mcp.get("name") == record.get("name")]
    if not matches:
        return None
    if expected_version:
        for mcp in matches:
            if versions_match(expected_version, mcp.get("version_pin")):
                return mcp
    if harness_names:
        for mcp in matches:
            if mcp.get("harness") in harness_names:
                return mcp
    return matches[0]


def _snapshot_skills(snapshot: dict, kinds: tuple[str, ...] | None = None) -> set[str]:
    """Skill names visible in the given store kinds (default: every store)."""
    names: set[str] = set()
    for store in snapshot.get("skill_stores", []):
        if kinds is not None and store.get("kind") not in kinds:
            continue
        for entry in store.get("entries", []):
            names.add(entry.get("name"))
    return names


def evaluate_profile(profile: dict, profiles: dict[str, dict], catalog: Catalog,
                      snapshot: dict | None, env_present: dict[str, bool] | None = None
                      ) -> dict:
    """Compare a profile against a local snapshot (read-only)."""
    resolved = resolved_components(profile, profiles)
    results: list[dict] = []
    counts: dict[str, int] = {}
    if snapshot is None:
        return {"profile": profile.get("id"), "results": results, "counts": counts}

    skills = _snapshot_skills(snapshot)
    canonical_skills = _snapshot_skills(snapshot, kinds=("canonical",))
    installed_plugins = {
        slug(str(p.get("name", "")).split("@")[0]) for p in snapshot.get("plugins", [])
    }
    harness_names = _profile_harness_names(profile, catalog)
    for category, items in resolved.items():
        for item in items:
            ref = item["ref"]
            requirement = item.get("requirement", "required")
            record = catalog.get(ref)
            if record is None:
                results.append({"ref": ref, "category": category, "status": "UNKNOWN",
                                "requirement": requirement,
                                "detail": "reference not found in inventory"})
                counts["UNKNOWN"] = counts.get("UNKNOWN", 0) + 1
                continue
            status, detail = "PRESENT", ""
            if requirement == "dynamic":
                owner = item.get("managed_by")
                owner_slug = slug(str(owner).split("-", 1)[-1]) if owner else ""
                present = (not owner_slug) or any(owner_slug[:10] in name for name in installed_plugins)
                results.append({
                    "ref": ref, "category": category,
                    "status": "DYNAMIC_PRESENT" if present else "DYNAMIC_MISSING",
                    "requirement": requirement, "detail": "injected by " + str(owner),
                    "ownership": item.get("ownership", "plugin_injected"),
                    "managed_by": owner,
                })
                counts["DYNAMIC_PRESENT" if present else "DYNAMIC_MISSING"] = counts.get(
                    "DYNAMIC_PRESENT" if present else "DYNAMIC_MISSING", 0) + 1
                continue
            if category == "harness":
                found = _snapshot_harness(snapshot, record)
                if not found or not found.get("installed"):
                    status, detail = "MISSING", "harness executable not found"
                elif item.get("version") and not versions_match(item["version"], found.get("version")):
                    status = "VERSION_MISMATCH"
                    detail = f"{found.get('version')} != {item['version']}"
            elif category == "plugin":
                found = _snapshot_plugin(snapshot, record)
                if not found:
                    status, detail = "MISSING", "plugin not installed"
                elif item.get("version") and not versions_match(item["version"], found.get("version")):
                    status = "VERSION_MISMATCH"
                    detail = f"{found.get('version')} != {item['version']}"
            elif category == "mcp":
                found = _snapshot_mcp(snapshot, record, harness_names, item.get("version"))
                if not found:
                    status, detail = "MISSING", "MCP not present in any harness config"
                elif item.get("version") and found.get("version_pin") and \
                        not versions_match(item["version"], found.get("version_pin")):
                    status = "VERSION_MISMATCH"
                    detail = f"{found.get('version_pin')} != {item['version']}"
            elif category == "skill":
                pool = canonical_skills if requirement == "canonical_shared" else skills
                if record.get("name") not in pool:
                    status, detail = "MISSING", "skill not present in any known skill store"
            elif category == "hook":
                owners = {
                    str(h.get("owner", "")).lower()
                    for h in snapshot.get("hooks", {}).get("hook_files", [])
                    if h.get("scope", "installed") == "installed"
                }
                owner = slug(item.get("managed_by") or record.get("name"))
                owner = owner[len("plugin-"):] if owner.startswith("plugin-") else owner
                if owners and not any(owner and owner in o for o in owners):
                    status, detail = "MISSING", "hook owner not present in plugin caches"
            if status == "MISSING" and requirement != "required":
                status = "OPTIONAL_MISSING"
                detail = (detail + " (optional)").strip()
            results.append({
                "ref": ref, "category": category, "status": status, "detail": detail,
                "requirement": requirement,
                "ownership": item.get("ownership", "directly_configured"),
                "managed_by": item.get("managed_by"),
            })
            counts[status] = counts.get(status, 0) + 1

    env_results = []
    for entry in (profile.get("environment_variables") or {}).get("required", []) or []:
        name = entry.get("name") if isinstance(entry, dict) else entry
        present = bool(env_present.get(name)) if env_present else None
        env_results.append({"name": name, "present": present,
                            "required_by": entry.get("required_by") if isinstance(entry, dict) else None})
        counts["ENV_PRESENT" if present else "ENV_MISSING"] = counts.get(
            "ENV_PRESENT" if present else "ENV_MISSING", 0) + 1

    deps = []
    for dep in profile.get("external_dependencies") or []:
        exists = None
        if snapshot:
            for entry in snapshot.get("external_dependencies", []):
                if entry.get("path") == dep.get("ref") or dep.get("ref") in entry.get("path", ""):
                    exists = entry.get("target_exists")
                    break
        deps.append({"ref": dep.get("ref"), "required": dep.get("required", False), "exists": exists})
        if exists is False and dep.get("required"):
            counts["MISSING"] = counts.get("MISSING", 0) + 1

    return {"profile": profile.get("id"), "results": results, "counts": counts,
            "environment_variables": env_results, "external_dependencies": deps}


# --------------------------------------------------------------------------- #
# Comparison, ownership, relationships
# --------------------------------------------------------------------------- #

def compare_profiles(a: dict, b: dict, profiles: dict[str, dict]) -> dict:
    ra = resolved_components(a, profiles)
    rb = resolved_components(b, profiles)
    diff: dict[str, dict] = {}
    for category in CATEGORIES:
        sa = {i["ref"] for i in ra[category]}
        sb = {i["ref"] for i in rb[category]}
        diff[category] = {
            "only_a": sorted(sa - sb),
            "only_b": sorted(sb - sa),
            "shared": len(sa & sb),
        }
    env_a = {e.get("name") for e in (a.get("environment_variables") or {}).get("required", []) or []}
    env_b = {e.get("name") for e in (b.get("environment_variables") or {}).get("required", []) or []}
    ext_a = {d.get("ref") for d in a.get("external_dependencies") or []}
    ext_b = {d.get("ref") for d in b.get("external_dependencies") or []}
    return {
        "profile_a": a.get("id"),
        "profile_b": b.get("id"),
        "components": diff,
        "environment_variables": {
            "only_a": sorted(env_a - env_b),
            "only_b": sorted(env_b - env_a),
            "shared": sorted(env_a & env_b),
        },
        "external_dependencies": {
            "only_a": sorted(ext_a - ext_b),
            "only_b": sorted(ext_b - ext_a),
        },
    }


def ownership_index(profiles: dict[str, dict], catalog: Catalog) -> dict:
    index: dict[str, dict] = {}
    for pid, profile in sorted(profiles.items()):
        for category, items in resolved_components(profile, profiles).items():
            for item in items:
                ref = item["ref"]
                record = catalog.get(ref) or {}
                entry = index.setdefault(ref, {
                    "category": category,
                    "name": record.get("name", ref),
                    "evidence_level": record.get("evidence_level"),
                    "canonical": category == "skill" and record.get("source_type") in
                                 {"skills-cli", "manual-or-unknown", "project-local-symlink"},
                    "divergent": category == "skill" and record.get("source_type") in
                                 {"manual-or-unknown"},
                    "profiles": [],
                    "ownership": [],
                    "managed_by": [],
                })
                if pid not in entry["profiles"]:
                    entry["profiles"].append(pid)
                ownership = item.get("ownership", "directly_configured")
                if ownership not in entry["ownership"]:
                    entry["ownership"].append(ownership)
                managed = item.get("managed_by")
                if managed and managed not in entry["managed_by"]:
                    entry["managed_by"].append(managed)
    return index


def relationships(profiles: dict[str, dict], catalog: Catalog) -> dict:
    rel: dict[str, dict] = {"profiles": {}, "plugins": {}, "harnesses": {}}
    for pid, profile in sorted(profiles.items()):
        resolved = resolved_components(profile, profiles)
        rel["profiles"][pid] = {
            category: [i["ref"] for i in items]
            for category, items in resolved.items() if items
        }
        rel["profiles"][pid]["external_dependencies"] = [
            d.get("ref") for d in profile.get("external_dependencies") or []
        ]
    # plugin -> injected MCP and provided skills (from inventory)
    for cid, record in catalog.entries.items():
        if record.get("category") == "mcp":
            injected_by = (record.get("entry") or {}).get("injected_by")
            if injected_by:
                rel["plugins"].setdefault(injected_by, {"injects_mcp": []})["injects_mcp"].append(cid)
        if record.get("category") == "skill":
            provided_by = (record.get("entry") or {}).get("provided_by")
            if provided_by and provided_by not in {"omp", "codex"}:
                rel["plugins"].setdefault(str(provided_by), {"provides_skills": []})
                rel["plugins"][str(provided_by)].setdefault("provides_skills", []).append(cid)
    for cid, record in catalog.entries.items():
        if record.get("category") == "skill" and record.get("source_type") == "harness-bundled":
            harness = str((record.get("entry") or {}).get("harnesses", ["codex"])[0])
            rel["harnesses"].setdefault(harness, {"built_in_skills": []})["built_in_skills"].append(cid)
    return rel


def env_var_presence(names: list[str]) -> dict[str, bool]:
    """Presence only. Values are never read or stored."""
    return {name: (name in os.environ) for name in names}


# --------------------------------------------------------------------------- #
# Applicability, extras and rendering
# --------------------------------------------------------------------------- #

def profile_applicable(profile: dict, catalog: Catalog, snapshot: dict | None) -> bool:
    """True when the profile's primary harness exists on this machine."""
    if snapshot is None:
        return True
    harnesses = (profile.get("harnesses") or {}).get("required") or []
    for item in harnesses:
        record = catalog.get(item.get("ref", ""))
        if record is None:
            continue
        command = (record.get("entry") or {}).get("command")
        for harness in snapshot.get("harnesses", []):
            if command and harness.get("name") == command and harness.get("installed"):
                return True
    return False


def profile_extras(profile: dict, profiles: dict[str, dict], catalog: Catalog,
                   snapshot: dict | None) -> dict[str, list[str]]:
    """Components installed locally that the profile does not mention (informational)."""
    extras: dict[str, list[str]] = {}
    if snapshot is None:
        return extras
    resolved = resolved_components(profile, profiles)
    for category in CATEGORIES:
        known = {i["ref"] for i in resolved[category]}
        names: set[str] = set()
        if category == "harness":
            names = {h.get("name") for h in snapshot.get("harnesses", []) if h.get("installed")}
        elif category == "plugin":
            names = {str(p.get("name", "")).split("@")[0] for p in snapshot.get("plugins", [])}
        elif category == "mcp":
            names = {m.get("name") for m in snapshot.get("mcps", [])}
        only = []
        for name in sorted(n for n in names if n):
            cid = component_id(category, name)
            if cid in known or cid in catalog.by_name.get((category, name), []):
                continue
            only.append(cid)
        if only:
            extras[category] = only
    return extras


def _component_table(profile: dict, profiles: dict[str, dict], catalog: Catalog,
                     category: str) -> list[str]:
    resolved = resolved_components(profile, profiles)
    lines = ["| Component | Requirement | Ownership | Version | Upstream |", "| --- | --- | --- | --- | --- |"]
    for item in resolved.get(category, []):
        record = catalog.get(item["ref"]) or {}
        version = item.get("version") or record.get("version") or ""
        upstream = record.get("upstream_repository") or ""
        lines.append(
            f"| `{item['ref']}` | {item.get('requirement', 'required')} | "
            f"{item.get('ownership', 'directly_configured')} | {version} | {upstream or 'unknown'} |"
        )
    if len(lines) == 2:
        lines.append("| _none_ | | | | |")
    return lines


def render_profile_doc(profile: dict, profiles: dict[str, dict], catalog: Catalog) -> str:
    pid = profile.get("id")
    repro = compute_reproducibility(profile, profiles, catalog)
    lines = [
        f"# Profile: {profile.get('name')} (`{pid}`)",
        "",
        f"- **Status:** {profile.get('status')}  ·  **Profile version:** {profile.get('profile_version')}",
        f"- **Reproducibility:** `{repro['status']}`",
        f"- **Evidence:** {profile.get('evidence_level')} (last verified {profile.get('last_verified')})",
        "",
        "## Purpose",
        "",
        profile.get("description", "").strip(),
        "",
        "## What this profile is not",
        "",
        "Declarative only. Loading a profile installs nothing, changes no configuration and starts "
        "no server. It is a checklist that can be compared with the current machine.",
        "",
        "## Installation order",
        "",
        "1. Runtime prerequisites (`requirements.commands`, minus the harness itself).",
        "2. Harness.",
        "3. Plugins (marketplace or npm resolver).",
        "4. Canonical skill store `~/.agents/skills`.",
        "5. Harness-specific skill stores and built-in skills.",
        "6. MCP packages and remote services.",
        "7. Sanitized configuration files.",
        "8. Verification (`./scripts/audit.sh --profile " + str(pid) + "`).",
        "",
        "## Harnesses",
        "",
    ]
    lines += _component_table(profile, profiles, catalog, "harnesses")
    lines += ["", "## Plugins", ""]
    lines += _component_table(profile, profiles, catalog, "plugins")
    lines += ["", "## MCP servers", ""]
    lines += _component_table(profile, profiles, catalog, "mcps")
    lines += ["", "## Skills", ""]
    lines += _component_table(profile, profiles, catalog, "skills")
    lines += ["", "## Hooks", ""]
    lines += _component_table(profile, profiles, catalog, "hooks")
    lines += ["", "## Environment variables (names only)", ""]
    env = profile.get("environment_variables") or {}
    for label in ("required", "optional"):
        names = [e.get("name") for e in env.get(label, []) or []]
        lines.append(f"- **{label.capitalize()}:** " + (", ".join(f"`{n}`" for n in names) if names else "_none_"))
    lines += ["", "## Requirements", ""]
    requirements = profile.get("requirements") or {}
    for label in ("commands", "files", "directories"):
        values = requirements.get(label) or []
        lines.append(f"- **{label.capitalize()}:** " + (", ".join(f"`{v}`" for v in values) if values else "_none_"))
    lines += ["", "## External dependencies", ""]
    deps = profile.get("external_dependencies") or []
    if deps:
        for dep in deps:
            lines.append(f"- `{dep.get('ref')}` (required: {dep.get('required', False)}) — {dep.get('reason', '')}")
    else:
        lines.append("_none_")
    lines += ["", "## Reproducibility", "", f"- **Status:** `{repro['status']}`"]
    if repro["reasons"]:
        lines.append("- **Reasons:**")
        lines += [f"  - {r}" for r in repro["reasons"]]
    if repro["blockers"]:
        lines.append("- **Blockers:**")
        lines += [f"  - {b}" for b in repro["blockers"]]
    if profile.get("notes"):
        lines += ["", "## Notes", "", profile["notes"].strip()]
    lines += ["", "## Related documentation", "",
              "- [Environment profiles](../profiles.md)",
              "- [Harnesses](../harnesses.md)",
              "- [MCP servers](../mcps.md)",
              "- [Plugins](../plugins.md)",
              "- [Hooks](../hooks.md)",
              "- [Installation guide](../installation.md)",
              "- [Inventory](../../inventory/)",
              ""]
    return "\n".join(lines)


def render_reproducibility_report(profiles: dict[str, dict], catalog: Catalog) -> str:
    rows = []
    detail = []
    for pid, profile in sorted(profiles.items()):
        repro = compute_reproducibility(profile, profiles, catalog)
        floating = repro.get("floating_versions") or []
        unresolved = len(profile.get("unresolved") or [])
        missing_prov = sum(
            1 for r in repro["reasons"] if "provenance unknown" in r
        )
        unknown_upstreams = sum(1 for r in repro["reasons"] if "upstream not verified" in r)
        private_deps = len(profile.get("external_dependencies") or [])
        rows.append(
            f"| `{pid}` | `{repro['status']}` | {missing_prov} | {len(floating)} | "
            f"{private_deps} | {unknown_upstreams} |"
        )
        detail.append(f"### `{pid}`")
        detail.append("")
        detail.append(f"- Status: `{repro['status']}`")
        for reason in repro["reasons"]:
            detail.append(f"- Reason: {reason}")
        for blocker in repro["blockers"]:
            detail.append(f"- Blocker: {blocker}")
        if not repro["reasons"] and not repro["blockers"]:
            detail.append("- No reproducibility caveats recorded.")
        detail.append("")
    lines = [
        "# Profile reproducibility",
        "",
        "Generated by `./scripts/audit.sh --profiles-report`. Status is computed from the "
        "profiles and the inventory; it never claims reproducibility that the evidence does "
        "not support.",
        "",
        "| Profile | Status | Missing provenance | Floating versions | Private dependencies | Unknown upstreams |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    lines += rows
    lines += ["", "## Detail", ""]
    lines += detail
    return "\n".join(lines).rstrip() + "\n"
