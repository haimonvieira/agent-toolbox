#!/usr/bin/env python3
"""
resolve_pins.py — Resolve o pin (repo + path + commit) de uma skill.

Para cada candidato, descobre:
  • licença do repositório
  • stars e data do último push
  • commit SHA do HEAD (o pin)
  • o caminho exato do SKILL.md dentro do repo

Saída: JSON com as entradas prontas para o catalog.json.

Uso:
  python3 resolve_pins.py            # resolve a lista CANDIDATES
  python3 resolve_pins.py --repo owner/name --skill nome
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

# (repo, nome da skill) — a lista curada
CANDIDATES = [
    # descoberta & meta (o tema que interessa neste chat)
    ("vercel-labs/skills", "find-skills"),
    ("obra/superpowers", "writing-skills"),
    ("mattpocock/skills", "writing-for-agents"),
    # engenharia / coding
    ("DietrichGebert/ponytail", "ponytail"),
    ("mattpocock/skills", "pr"),
    ("obra/superpowers", "systematic-debugging"),
    ("obra/superpowers", "verification-before-completion"),
    ("obra/superpowers", "writing-plans"),
    ("obra/superpowers", "test-driven-development"),
    # mapear codebase
    ("github/awesome-copilot", "acquire-codebase-knowledge"),
    # devops
    ("jeffallan/claude-skills", "devops-engineer"),
    ("mrgoonie/claudekit-skills", "devops"),
]

API = "https://api.github.com"


def _headers():
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "agent-toolbox-resolver",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def api_get(url, retries=3):
    for attempt in range(retries):
        req = urllib.request.Request(url, headers=_headers())
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return {"_error": "404"}
            if exc.code in (403, 429) and attempt < retries - 1:
                time.sleep(20)
                continue
            return {"_error": f"HTTP {exc.code}"}
        except Exception as exc:
            if attempt < retries - 1:
                time.sleep(5)
                continue
            return {"_error": str(exc)[:120]}
    return {"_error": "esgotou tentativas"}


def head_sha(repo_url):
    """Pega o SHA do HEAD do branch default via git ls-remote (não consome API)."""
    try:
        out = subprocess.run(
            ["git", "ls-remote", repo_url, "HEAD"],
            capture_output=True, text=True, timeout=40,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.split()[0]
    except Exception:
        pass
    return None


def find_skill_path(tree, skill_name):
    """Localiza o SKILL.md da skill. Prefere skills/<nome>/, depois qualquer <nome>/."""
    paths = [it["path"] for it in tree if it["path"].endswith("SKILL.md")]
    low = skill_name.lower()

    # 1. skills/<nome>/SKILL.md
    for p in paths:
        if p.lower() == f"skills/{low}/skill.md":
            return p
    # 2. <qualquer>/<nome>/SKILL.md (ignora espelhos tipo .openclaw/)
    cands = [p for p in paths if f"/{low}/skill.md" in p.lower() and not p.startswith(".")]
    if cands:
        return sorted(cands, key=len)[0]
    # 3. contém o nome
    cands = [p for p in paths if low in p.lower()]
    if cands:
        return sorted(cands, key=len)[0]
    return None


def resolve(repo, skill_name):
    print(f"  {repo} :: {skill_name}", file=sys.stderr)
    entry = {"repo": f"https://github.com/{repo}", "slug": repo, "skill": skill_name}

    meta = api_get(f"{API}/repos/{repo}")
    if "_error" in meta:
        entry["error"] = f"repo: {meta['_error']}"
        return entry

    entry["license"] = (meta.get("license") or {}).get("spdx_id") or None
    entry["stars"] = meta.get("stargazers_count")
    entry["pushed_at"] = (meta.get("pushed_at") or "")[:10]
    entry["description"] = meta.get("description")

    sha = head_sha(f"https://github.com/{repo}")
    if not sha:
        entry["error"] = "não consegui o HEAD sha"
        return entry
    entry["commit"] = sha

    tree = api_get(f"{API}/repos/{repo}/git/trees/{sha}?recursive=1")
    if "_error" in tree:
        entry["error"] = f"tree: {tree['_error']}"
        return entry

    path = find_skill_path(tree.get("tree", []), skill_name)
    if not path:
        entry["error"] = "SKILL.md não encontrado"
        return entry
    entry["path"] = path
    entry["installable"] = True
    entry["license_ok_to_copy"] = entry["license"] in ("MIT", "Apache-2.0", "BSD-3-Clause", "ISC")
    return entry


def main():
    if "--repo" in sys.argv:
        repo = sys.argv[sys.argv.index("--repo") + 1]
        skill = sys.argv[sys.argv.index("--skill") + 1]
        print(json.dumps(resolve(repo, skill), indent=2, ensure_ascii=False))
        return 0

    results = []
    for repo, skill in CANDIDATES:
        results.append(resolve(repo, skill))
        time.sleep(1.2)  # gentileza com a API

    print(json.dumps(results, indent=2, ensure_ascii=False))
    ok = sum(1 for r in results if r.get("installable"))
    print(f"\n# {ok}/{len(results)} resolvidas com pin", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())