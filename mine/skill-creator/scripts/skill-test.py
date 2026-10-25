#!/usr/bin/env python3
"""
skill-test.py — Executa testes programáticos em uma skill.

Suporta dois modos:
  1. Declarativo: lê tests/test-cases.json e compara saída com esperado
  2. Scripts: executa cada script em scripts/ com entradas de teste

Uso:
  python3 skill-test.py <caminho-da-skill>
  python3 skill-test.py <caminho-da-skill> --verbose

Formato de tests/test-cases.json:
{
  "cases": [
    {
      "name": "entrada-valida",
      "input": {"script": "processar.py", "args": ["--modo", "rapido"], "stdin": "dados.txt"},
      "expect": {"exit": 0, "contains": ["relatorio"], "not_contains": ["erro"]}
    }
  ]
}

Exit codes:
  0  = todos os testes passaram
  1  = falhas
  64 = uso incorreto
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run_script(script_path: Path, args: list, stdin_text: str = None, timeout: int = 60):
    """Executa um script e retorna (exit_code, stdout, stderr)."""
    cmd = [sys.executable, str(script_path)] + args
    proc = subprocess.run(
        cmd,
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(script_path.parent),
    )
    return proc.returncode, proc.stdout, proc.stderr


def assert_case(case: dict, skill_dir: Path) -> tuple[bool, str]:
    """Executa uma assertiva de teste. Retorna (sucesso, mensagem)."""
    inp = case.get("input", {})
    script_name = inp.get("script")
    if not script_name:
        return False, "caso sem 'input.script' definido"

    script_path = skill_dir / "scripts" / script_name
    if not script_path.exists():
        return False, f"script '{script_name}' não encontrado"

    args = inp.get("args", [])
    stdin = inp.get("stdin")

    try:
        exit_code, stdout, stderr = run_script(script_path, args, stdin)
    except subprocess.TimeoutExpired:
        return False, f"script '{script_name}' excedeu o timeout"
    except Exception as exc:  # pragma: no cover
        return False, f"erro ao executar {script_name}: {exc}"

    expect = case.get("expect", {})

    # Verifica exit code
    if "exit" in expect and exit_code != expect["exit"]:
        return (
            False,
            f"exit code {exit_code} (esperado {expect['exit']})\nstdout: {stdout[:300]}\nstderr: {stderr[:300]}",
        )

    # Verifica contém
    combined = stdout + stderr
    for needle in expect.get("contains", []):
        if needle not in combined:
            return False, f"saída não contém '{needle}'"

    # Verifica não contém
    for needle in expect.get("not_contains", []):
        if needle in combined:
            return False, f"saída contém indevidamente '{needle}'"

    # Verifica arquivo de saída
    for out_file in expect.get("output_files", []):
        out_path = skill_dir / out_file
        if not out_path.exists():
            return False, f"arquivo de saída '{out_file}' não foi gerado"

    return True, f"exit={exit_code}, stdout={len(stdout)} chars"


def run_tests(skill_dir: Path, verbose: bool = False) -> dict:
    """Executa todos os testes da skill. Retorna relatório."""
    report = {
        "skill": skill_dir.name,
        "total": 0,
        "passed": 0,
        "failed": 0,
        "results": [],
    }

    # Modo 1: test-cases.json
    test_file = skill_dir / "tests" / "test-cases.json"
    if test_file.exists():
        try:
            cases = json.loads(test_file.read_text(encoding="utf-8")).get("cases", [])
        except (json.JSONDecodeError, KeyError) as exc:
            report["results"].append({
                "name": "parse-test-cases",
                "success": False,
                "message": f"falha ao parsear test-cases.json: {exc}",
            })
            report["total"] += 1
            report["failed"] += 1
            return report

        for case in cases:
            report["total"] += 1
            success, message = assert_case(case, skill_dir)
            report["results"].append({
                "name": case.get("name", "anonimo"),
                "success": success,
                "message": message,
            })
            if success:
                report["passed"] += 1
            else:
                report["failed"] += 1

    # Modo 2: scripts auto-testáveis (scripts com --help ou que podem rodar sem args)
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for script in sorted(scripts_dir.glob("*.py")):
            # scripts de suporte (.py que começam com _) ou o próprio skill-test
            if script.name.startswith("_"):
                continue
            # Só testa se houver test-cases.json; senão apenas reporta existência
            if not test_file.exists():
                if verbose:
                    report["results"].append({
                        "name": f"scripts/{script.name}",
                        "success": None,
                        "message": "script presente mas sem test-case definido",
                    })

    if report["total"] == 0:
        report["results"].append({
            "name": "test-discovery",
            "success": None,
            "message": "nenhum test-case definido. Crie tests/test-cases.json.",
        })

    return report


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    verbose = "--verbose" in sys.argv

    if not args:
        print("Uso: skill-test.py <caminho-da-skill> [--verbose]", file=sys.stderr)
        sys.exit(64)

    skill_dir = Path(args[0])
    if not skill_dir.is_dir():
        print(f"ERRO: '{skill_dir}' não é um diretório.", file=sys.stderr)
        sys.exit(64)

    report = run_tests(skill_dir, verbose)

    print(f"Skill: {report['skill']}")
    print(f"Testes: {report['total']} | Passou: {report['passed']} | Falhou: {report['failed']}")
    for res in report["results"]:
        icon = "✅" if res["success"] else ("⚠️" if res["success"] is None else "❌")
        print(f"  {icon} {res['name']}: {res['message']}")

    if report["failed"] > 0:
        sys.exit(1)
    if report["total"] == 0:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()