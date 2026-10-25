#!/usr/bin/env python3
"""
parse_logs.py — Analisa logs de aplicação e extrai informações estruturadas.

Entrada: log via stdin (ou arquivo passado como argumento)
Saída: JSON para stdout com:
  {
    "total_lines": int,
    "error_lines": int,
    "errors": [{"level": str, "timestamp": str, "message": str, "component": str}],
    "frequency": {"mensagem": ocorrencias},
    "time_window": {"start": str, "end": str},
    "root_cause_candidate": str,
    "severity": "CRITICA|ALTA|MEDIA|BAIXA",
    "known_pattern": str ou null
  }

Uso:
  cat app.log | python3 parse_logs.py [--known-patterns FILE]
  python3 parse_logs.py app.log [--known-patterns FILE]

Exit codes:
  0  = análise concluída (pode ter 0 erros)
  1  = entrada vazia ou ilegível
  2  = erro interno
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime

# Níveis de log (ordem de gravidade)
LEVEL_ORDER = {"FATAL": 5, "ERROR": 4, "WARN": 3, "WARNING": 3, "INFO": 2, "DEBUG": 1, "TRACE": 0}

# Padrão de timestamp ISO ou comum: 2024-01-15 10:30:45,123 ou 2024-01-15T10:30:45.123Z
TIMESTAMP_PATTERNS = [
    re.compile(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"),
    re.compile(r"(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})"),
]

# Padrão de nível de log
LEVEL_RE = re.compile(r"\b(FATAL|ERROR|WARN|WARNING|INFO|DEBUG|TRACE)\b")

# Componente entre colchetes: [payment-service]
COMPONENT_RE = re.compile(r"\[([a-zA-Z0-9._-]+)\]")

# Mensagem após o nível
MSG_RE = re.compile(r"\b(?:FATAL|ERROR|WARN|WARNING|INFO|DEBUG|TRACE)\b\s*[-:]*\s*(.*)")

# Padrões de erro conhecidos
COMMON_PATTERNS = [
    (r"OutOfMemoryError|heap space", "Vazamento de memória / falta de heap"),
    (r"Connection refused|Connection reset|Connection timeout", "Falha de conexão com dependência"),
    (r"NullPointerException|NoneType|undefined is not", "Referência nula / valor ausente"),
    (r"DatabaseDeadlock|deadlock|locked for update", "Deadlock no banco de dados"),
    (r"RateLimit|429|rate limit", "Limite de taxa excedido"),
    (r"SQLSyntax|syntax error|SQL exception", "Erro de SQL / schema"),
    (r"SSL|certificate|TLS", "Problema de certificado/SSL"),
    (r"Timeout|timed out", "Timeout de operação"),
    (r"Unauthorized|401|forbidden|auth failed", "Falha de autenticação"),
    (r"500|502|503|504", "Erro HTTP no servidor"),
]


def parse_timestamp(line: str) -> str:
    for pat in TIMESTAMP_PATTERNS:
        m = pat.search(line)
        if m:
            return m.group(1)
    return ""


def parse_line(line: str) -> dict:
    level_m = LEVEL_RE.search(line)
    level = level_m.group(1) if level_m else ""

    comp_m = COMPONENT_RE.search(line)
    component = comp_m.group(1) if comp_m else ""

    msg_m = MSG_RE.search(line)
    message = msg_m.group(1).strip() if msg_m else line.strip()[:120]

    return {
        "level": level,
        "timestamp": parse_timestamp(line),
        "message": message,
        "component": component,
    }


def classify_severity(errors: list, total_lines: int) -> str:
    if not errors:
        return "BAIXA"
    levels = [e["level"] for e in errors]
    if "FATAL" in levels:
        return "CRITICA"
    if len(errors) > total_lines * 0.1:
        return "ALTA"
    if len(errors) > 5:
        return "MEDIA"
    return "BAIXA"


def find_known_pattern(errors: list) -> str:
    all_text = " ".join(e["message"] for e in errors)
    for pattern, label in COMMON_PATTERNS:
        if re.search(pattern, all_text, re.IGNORECASE):
            return label
    return None


def find_root_cause(errors: list) -> str:
    """O erro raiz é o primeiro erro cronologicamente (ou o mais grave dos primeiros)."""
    if not errors:
        return "Nenhum erro detectado"
    # Ordena por timestamp; o primeiro é o candidato a causa raiz
    with_ts = [e for e in errors if e["timestamp"]]
    if with_ts:
        with_ts.sort(key=lambda e: e["timestamp"])
        first = with_ts[0]
    else:
        first = errors[0]
    return f"{first['level']} em {first['component'] or 'desconhecido'}: {first['message'][:100]}"


def analyze(lines: list) -> dict:
    parsed = [parse_line(l) for l in lines if l.strip()]
    errors = [p for p in parsed if p["level"] and LEVEL_ORDER.get(p["level"], 0) >= 4]

    frequency = Counter(e["message"][:80] for e in errors)

    return {
        "total_lines": len(parsed),
        "error_lines": len(errors),
        "errors": errors,
        "frequency": dict(frequency.most_common(10)),
        "time_window": {
            "start": errors[0]["timestamp"] if errors else "",
            "end": errors[-1]["timestamp"] if errors else "",
        },
        "root_cause_candidate": find_root_cause(errors),
        "severity": classify_severity(errors, len(parsed)),
        "known_pattern": find_known_pattern(errors),
    }


def main():
    parser = argparse.ArgumentParser(description="Analisa logs de aplicacao e extrai informacoes estruturadas.")
    parser.add_argument("file", nargs="?", help="Arquivo de log (se omitido, lê stdin)")
    parser.add_argument("--known-patterns", help="Arquivo JSON com padroes conhecidos (opcional)")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError as exc:
            print(json.dumps({"error": f"nao foi possível ler o arquivo: {exc}"}, ensure_ascii=False), file=sys.stderr)
            return 1
    else:
        if sys.stdin.isatty():
            print("Uso: cat log.txt | python3 parse_logs.py ou python3 parse_logs.py arquivo.log", file=sys.stderr)
            return 1
        lines = sys.stdin.readlines()

    if not lines or not any(l.strip() for l in lines):
        print(json.dumps({"error": "entrada vazia — nenhum log fornecido"}, ensure_ascii=False), file=sys.stderr)
        return 1

    try:
        result = analyze(lines)
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"error": f"erro interno: {exc}"}, ensure_ascii=False), file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())