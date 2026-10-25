#!/usr/bin/env python3
"""
emit_config.py — Gera a configuração de MCP para o agente escolhido.

Lê catalog.json e emite a configuração no formato nativo de omp, Claude Code
ou OpenCode. Não modifica nada sem --write.

Uso:
  python3 scripts/emit_config.py --tool omp
  python3 scripts/emit_config.py --tool opencode
  python3 scripts/emit_config.py --tool claude-code

  # gravar no arquivo do projeto (sobrescreve o bloco mcp/mcpServers)
  python3 scripts/emit_config.py --tool omp --write

  # só um servidor
  python3 scripts/emit_config.py --tool opencode --only omgskills

Opções:
  --tool    omp | claude-code | opencode   (obrigatório)
  --only    nome de um servidor específico
  --write   grava no arquivo em vez de imprimir
  --out     caminho alternativo de saída
"""

import json
import os
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"
TOOLS = ROOT / "data" / "tools.json"

PLACEHOLDER = "COLE_O_VALOR_AQUI"

DEFAULT_PATHS = {
    "omp": ".omp/mcp.json",
    "claude-code": ".mcp.json",
    "opencode": "opencode.json",
}


def parse_args(argv):
    opts = {"tool": None, "only": None, "write": False, "out": None}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--tool":
            opts["tool"] = argv[i + 1]; i += 2
        elif a == "--only":
            opts["only"] = argv[i + 1]; i += 2
        elif a == "--out":
            opts["out"] = argv[i + 1]; i += 2
        elif a == "--write":
            opts["write"] = True; i += 1
        elif a in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        else:
            i += 1
    return opts


def build_entry(m, tool_id):
    env = {v: PLACEHOLDER for v in m["env_vars"]}
    headers = {h: f"Bearer {PLACEHOLDER}" for h in m["header_names"]}
    is_http = m["transport"] == "http"

    if tool_id in ("omp", "claude-code"):
        if is_http:
            e = {"type": "http", "url": m["url"]}
            if headers:
                e["headers"] = headers
            return e
        e = {"command": m["command"]}
        if m["args"]:
            e["args"] = m["args"]
        if env:
            e["env"] = env
        return e

    if tool_id == "opencode":
        if is_http:
            e = {"type": "remote", "url": m["url"], "enabled": True}
            if headers:
                e["headers"] = headers
            return e
        e = {"type": "local", "command": [m["command"]] + m["args"], "enabled": True}
        if env:
            e["environment"] = env
        return e

    raise SystemExit(f"ferramenta desconhecida: {tool_id}")


def main():
    opts = parse_args(sys.argv[1:])
    if not opts["tool"]:
        print("ERRO: informe --tool omp|claude-code|opencode", file=sys.stderr)
        return 2
    if opts["tool"] not in DEFAULT_PATHS:
        print(f"ERRO: --tool deve ser omp, claude-code ou opencode", file=sys.stderr)
        return 2

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    mcps = catalog["mcps"]
    if opts["only"]:
        mcps = [m for m in mcps if m["name"] == opts["only"]]
        if not mcps:
            print(f"ERRO: servidor '{opts['only']}' não está no catálogo", file=sys.stderr)
            return 2

    if opts["tool"] == "claude-code":
        # Claude Code tem comando próprio; imprime comandos em vez de JSON
        linhas = []
        for m in mcps:
            args = ["claude", "mcp", "add"]
            if m["transport"] == "http":
                args += ["--transport", "http", m["name"], m["url"]]
                for h in m["header_names"]:
                    args += ["--header", f"{h}: Bearer {PLACEHOLDER}"]
            else:
                for v in m["env_vars"]:
                    args += ["--env", f"{v}={PLACEHOLDER}"]
                args += [m["name"], "--", m["command"]] + m["args"]
            linhas.append(" ".join(shlex.quote(a) for a in args))
        saida = "\n".join(linhas)
    else:
        chave = "mcp" if opts["tool"] == "opencode" else "mcpServers"
        bloco = {chave: {m["name"]: build_entry(m, opts["tool"]) for m in mcps}}
        saida = json.dumps(bloco, indent=2, ensure_ascii=False)

    if not opts["write"] or opts["tool"] == "claude-code":
        print(saida)
        if not opts["write"]:
            print()
            print(f"# padrão para este agente: {DEFAULT_PATHS[opts['tool']]}", file=sys.stderr)
            print("# use --write para gravar", file=sys.stderr)
        return 0

    destino = Path(opts["out"] or DEFAULT_PATHS[opts["tool"]])
    destino.parent.mkdir(parents=True, exist_ok=True)

    # preserva outras chaves do arquivo existente
    existente = {}
    if destino.exists():
        try:
            existente = json.loads(destino.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"AVISO: {destino} não é JSON válido; não vou sobrescrever.", file=sys.stderr)
            return 1
    chave = "mcp" if opts["tool"] == "opencode" else "mcpServers"
    existente.setdefault(chave, {}).update(json.loads(saida)[chave])
    destino.write_text(json.dumps(existente, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{destino}: {len(mcps)} servidor(es) gravado(s) sob a chave '{chave}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
