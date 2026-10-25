#!/usr/bin/env python3
"""
verify_pins.py — Verifica os pins das recomendações em catalog.json.

Para cada skill recomendada, confere:
  • o commit pinado ainda existe no repositório?
  • o SKILL.md ainda está no caminho declarado, naquele commit?
  • houve push depois do pin? (indica que a ficha pode estar defasada)

A API pública do GitHub permite 60 requisições por hora sem autenticação. Se o
limite for atingido, o script reporta "não verificado" em vez de acusar o commit
como inexistente — a diferença importa.

Exit codes:
  0 = todos os pins verificados e válidos
  1 = algum pin realmente quebrado
  2 = não foi possível verificar tudo (rede ou limite de requisições)

Uso:
  python3 scripts/verify_pins.py [--quiet]
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"

# Resultados possíveis de uma verificação
EXISTS = "existe"
MISSING = "ausente"
UNKNOWN = "indeterminado"   # rede fora, limite de requisições, etc.


def _headers():
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "agent-toolbox-verifier",
    }
    # Usa o token se existir: eleva o limite de 60 para 5000 req/h.
    # O valor nunca é impresso nem gravado.
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def api_get(url, retries=2):
    """GET na API do GitHub. Retorna (dados, estado) onde estado é EXISTS/MISSING/UNKNOWN."""
    for attempt in range(retries):
        req = urllib.request.Request(url, headers=_headers())
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode()), EXISTS
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None, MISSING
            if exc.code in (403, 429):
                # limite de requisições da API pública
                if attempt < retries - 1:
                    time.sleep(20)
                    continue
                return None, UNKNOWN
            return None, UNKNOWN
        except Exception:
            if attempt < retries - 1:
                time.sleep(5)
                continue
            return None, UNKNOWN
    return None, UNKNOWN


def head_sha(repo_url):
    """SHA do HEAD do branch padrão, via git ls-remote (não consome a API)."""
    try:
        out = subprocess.run(["git", "ls-remote", repo_url, "HEAD"],
                             capture_output=True, text=True, timeout=40)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.split()[0]
    except Exception:
        pass
    return None


def main():
    quiet = "--quiet" in sys.argv
    if not CATALOG.exists():
        print("ERRO: catalog.json não encontrado. Rode scripts/build.py primeiro.", file=sys.stderr)
        return 2

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = catalog.get("recommended", [])

    counts = {EXISTS: 0, MISSING: 0, UNKNOWN: 0}
    drifted = 0
    problems = []

    for s in entries:
        repo = s["repo"].replace("https://github.com/", "")
        sha, path, name = s["commit"], s["path"], s["name"]

        if not quiet:
            print(f"  {name:<32}", end="", flush=True)

        _, state = api_get(f"https://api.github.com/repos/{repo}/commits/{sha}")
        if state != EXISTS:
            counts[state] += 1
            if state == MISSING:
                problems.append(f"{name}: commit {sha[:12]} não existe em {repo}")
                if not quiet:
                    print("commit ausente")
            else:
                problems.append(f"{name}: não verificado (limite de requisições ou rede)")
                if not quiet:
                    print("não verificado")
            continue

        _, pstate = api_get(f"https://api.github.com/repos/{repo}/contents/{path}?ref={sha}")
        if pstate == MISSING:
            counts[MISSING] += 1
            problems.append(f"{name}: '{path}' ausente no commit {sha[:12]}")
            if not quiet:
                print("caminho ausente")
            continue
        if pstate == UNKNOWN:
            counts[UNKNOWN] += 1
            problems.append(f"{name}: caminho não verificado")
            if not quiet:
                print("caminho não verificado")
            continue

        current = head_sha(f"https://github.com/{repo}")
        if current and current != sha:
            drifted += 1
            if not quiet:
                print(f"defasado (HEAD em {current[:12]})")
        else:
            counts[EXISTS] += 1
            if not quiet:
                print("ok")

        time.sleep(1.0)

    print()
    print(f"válidos:            {counts[EXISTS]}")
    print(f"válidos, defasados: {drifted}")
    print(f"quebrados:          {counts[MISSING]}")
    print(f"não verificados:    {counts[UNKNOWN]}")

    if problems:
        print("\nOcorrências:")
        for p in problems:
            print(f"  {p}")

    if counts[MISSING]:
        return 1
    if counts[UNKNOWN]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
