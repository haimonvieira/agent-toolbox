#!/usr/bin/env python3
"""
skill-server.py — Servidor MCP (JSON-RPC over stdio) para criação e gestão de skills.

Expõe ferramentas para agentes de IA:
  • create_skill        — cria a estrutura completa de uma skill nova
  • validate_skill      — valida frontmatter, seções e referências
  • test_skill          — executa os testes declarados da skill
  • list_skills         — lista skills instaladas com metadados
  • read_skill          — lê o SKILL.md de uma skill
  • get_skill_template  — devolve o template anotado para escrever skills
  • update_skill        — atualiza frontmatter (versão, descrição) de uma skill

Protocolo: MCP 2024-11-05 (JSON-RPC 2.0) via stdin/stdout.
Dependências: nenhuma além da stdlib do Python 3.8+.

Uso (como servidor MCP stdio):
  python3 skill-server.py
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Onde as skills vivem (pode ser sobrescrito pelo ambiente).
SKILLS_ROOT = Path(os.environ.get("SKILLS_ROOT", Path.home() / ".agent-skills"))

# Onde este pacote vive. Os validadores são procurados ao lado deste arquivo,
# não sob SKILLS_ROOT — assim o servidor funciona de qualquer diretório.
SELF_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SELF_DIR / "scripts"

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "skill-creator-server"
SERVER_VERSION = "1.0.0"


# --------------------------------------------------------------------------
# Núcleo: lógica de skills
# --------------------------------------------------------------------------

def _valid_name(name: str) -> bool:
    return bool(re.match(r"^[a-z][a-z0-9_-]*$", name or ""))


def _skill_dir(name: str) -> Path:
    return SKILLS_ROOT / name


def create_skill(name: str, description: str, sections: dict = None,
                 with_tests: bool = True, force: bool = False) -> dict:
    """Cria a estrutura de uma skill nova."""
    if not _valid_name(name):
        return {"ok": False, "error": f"Nome inválido '{name}'. Use [a-z][a-z0-9_-]*."}

    target = _skill_dir(name)
    if target.exists() and not force:
        return {"ok": False, "error": f"A skill '{name}' já existe em {target}. Use force=true para sobrescrever."}

    sections = sections or {}
    target.mkdir(parents=True, exist_ok=True)
    for sub in ("scripts", "references", "assets"):
        (target / sub).mkdir(exist_ok=True)

    if with_tests:
        (target / "tests").mkdir(exist_ok=True)

    # Frontmatter
    desc = (description or "").strip() or (
        "Descreva o objetivo da skill e quando ela deve ser ativada. "
        "Inclua variações de linguagem do usuário e condições de exclusão. "
        "Este campo é o mecanismo principal de ativação — seja exaustivo."
    )

    body_sections = {
        "Quando usar": sections.get("quando_usar", "### Gatilhos\n-\n\n### Não usar\n-"),
        "Fronteira do fluxo": sections.get(
            "fronteira",
            "### Entrada\n-\n\n### Passos\n1.\n2.\n3.\n\n### Saída\n-\n\n"
            "### Proibições\n- NÃO\n\n### Pontos de parada\n- PERGUNTE se\n- RECUSE se",
        ),
        "Integração MCP": sections.get(
            "mcp",
            "### Servidores necessários\n| Servidor | Ferramenta | Propósito | Auth |\n|---|---|---|---|\n| | | | |\n\n"
            "### Tratamento de erro\n| Situação | Ação |\n|---|---|\n| | |",
        ),
        "Recursos auxiliares": sections.get(
            "recursos",
            "- `references/` — consulte quando:\n- `scripts/` — execute quando:\n- `assets/` — use como template para:",
        ),
        "Critérios de sucesso": sections.get("criterios", "-"),
    }

    test_table = (
        "| # | Tipo | Entrada | Comportamento esperado |\n|---|---|---|---|\n"
        "| 1 | Direto | | |\n| 2 | Indireto | | |\n| 3 | Incompleto | | |\n"
        "| 4 | Negativo | | |\n| 5 | Borda | | |"
    ) if with_tests else "_(sem testes declarados)_"

    content = f"""---
name: {name}
description: >
  {desc}
metadata:
  version: "1.0.0"
---

# {name}

"""
    for title, section_body in body_sections.items():
        content += f"## {title}\n\n{section_body}\n\n"
    content += f"## Casos de teste\n\n{test_table}\n"

    (target / "SKILL.md").write_text(content, encoding="utf-8")

    created = ["SKILL.md", "scripts/", "references/", "assets/"]
    if with_tests:
        created.append("tests/")

    return {
        "ok": True,
        "path": str(target),
        "created": created,
        "next_steps": [
            "Preencha a descrição do frontmatter (gatilho principal)",
            "Defina passos, proibições e pontos de parada",
            "Adicione recursos em scripts/, references/, assets/",
            "Execute validate_skill e test_skill",
        ],
    }


def validate_skill(name: str, strict: bool = False) -> dict:
    """Valida uma skill usando skill-validate.py."""
    script = SCRIPTS_DIR / "skill-validate.py"
    if not script.exists():
        return {"ok": False, "error": f"skill-validate.py não encontrado em {SCRIPTS_DIR}"}

    target = _skill_dir(name)
    if not target.is_dir():
        return {"ok": False, "error": f"Skill '{name}' não encontrada."}

    cmd = [sys.executable, str(script), str(target), "--json"]
    if strict:
        cmd.append("--strict")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout na validação"}

    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": f"saída inválida: {proc.stdout[:300]} {proc.stderr[:300]}"}

    return {"ok": True, "skill": name, **result}


def test_skill(name: str) -> dict:
    """Executa os testes de uma skill usando skill-test.py."""
    script = SCRIPTS_DIR / "skill-test.py"
    if not script.exists():
        return {"ok": False, "error": f"skill-test.py não encontrado em {SCRIPTS_DIR}"}

    target = _skill_dir(name)
    if not target.is_dir():
        return {"ok": False, "error": f"Skill '{name}' não encontrada."}

    try:
        proc = subprocess.run(
            [sys.executable, str(script), str(target)],
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout nos testes"}

    return {
        "ok": proc.returncode == 0,
        "skill": name,
        "exit_code": proc.returncode,
        "output": proc.stdout.strip(),
        "stderr": proc.stderr.strip()[:500] if proc.stderr else "",
    }


def list_skills() -> dict:
    """Lista skills instaladas com metadados do frontmatter."""
    if not SKILLS_ROOT.is_dir():
        return {"ok": False, "error": f"{SKILLS_ROOT} não existe."}

    skills = []
    for entry in sorted(SKILLS_ROOT.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        skill_md = entry / "SKILL.md"
        meta = {"name": entry.name, "path": str(entry), "has_skill_md": skill_md.exists()}
        if skill_md.exists():
            try:
                content = skill_md.read_text(encoding="utf-8")[:2000]
                m = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
                # versão pode estar em topo ou em metadata.version
                v = (re.search(r"^version:\s*(.+)$", content, re.MULTILINE)
                     or re.search(r"^\s+version:\s*(.+)$", content, re.MULTILINE))
                if not v and re.search(r"^metadata:", content, re.MULTILINE):
                    pass  # sem versão declarada dentro de metadata
                meta["declared_name"] = m.group(1).strip().strip('"') if m else None
                meta["version"] = v.group(1).strip().strip('"') if v else None
            except OSError:
                pass
        for sub in ("scripts", "references", "assets"):
            d = entry / sub
            meta[f"has_{sub}"] = d.is_dir() and any(d.iterdir())
        skills.append(meta)

    return {"ok": True, "count": len(skills), "skills": skills}


def read_skill(name: str, max_chars: int = 20000) -> dict:
    """Lê o SKILL.md de uma skill."""
    skill_md = _skill_dir(name) / "SKILL.md"
    if not skill_md.exists():
        return {"ok": False, "error": f"SKILL.md não encontrado para '{name}'."}
    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
    truncated = len(content) > max_chars
    return {
        "ok": True, "name": name,
        "content": content[:max_chars],
        "truncated": truncated,
        "total_chars": len(content),
    }


def get_skill_template() -> dict:
    """Devolve o template anotado de skill."""
    tpl = SELF_DIR / "references" / "skill-template.md"
    if tpl.exists():
        return {"ok": True, "source": str(tpl), "content": tpl.read_text(encoding="utf-8")}

    return {
        "ok": True,
        "source": "builtin",
        "content": (
            "---\nname: nome-da-skill\nversion: 1.0.0\ndescription: >\n  ...\n---\n\n"
            "# Nome\n\n## Quando usar\n### Gatilhos\n-\n### Não usar\n-\n\n"
            "## Fronteira do fluxo\n### Entrada\n-\n### Passos\n1.\n### Saída\n-\n"
            "### Proibições\n- NÃO\n### Pontos de parada\n- PERGUNTE se\n\n"
            "## Recursos auxiliares\n- `references/`\n- `scripts/`\n- `assets/`\n\n"
            "## Critérios de sucesso\n-\n\n## Casos de teste\n| # | Tipo | Entrada | Esperado |\n|---|---|---|---|\n"
            "| 1 | Direto | | |\n| 2 | Indireto | | |\n| 3 | Incompleto | | |\n"
            "| 4 | Negativo | | |\n| 5 | Borda | | |\n"
        ),
    }


def update_skill(name: str, version: str = None, description: str = None) -> dict:
    """Atualiza o frontmatter de uma skill (version e/ou description)."""
    skill_md = _skill_dir(name) / "SKILL.md"
    if not skill_md.exists():
        return {"ok": False, "error": f"SKILL.md não encontrado para '{name}'."}

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {"ok": False, "error": "SKILL.md não tem frontmatter válido."}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {"ok": False, "error": "Frontmatter malformado."}

    fm_text, body = parts[1], parts[2]
    changed = []

    if version:
        # Prefere metadata.version (spec Claude); mantém o topo se já existir lá.
        # Usa [ \t]+ (e não \s+) para não consumir quebras de linha.
        if re.search(r"^[ \t]+version:.*$", fm_text, re.MULTILINE) and re.search(r"^metadata:", fm_text, re.MULTILINE):
            fm_text = re.sub(r"^([ \t]+)version:.*$", rf'\g<1>version: "{version}"', fm_text, flags=re.MULTILINE)
        elif re.search(r"^version:.*$", fm_text, re.MULTILINE):
            fm_text = re.sub(r"^version:.*$", f'version: "{version}"', fm_text, flags=re.MULTILINE)
        elif re.search(r"^metadata:.*$", fm_text, re.MULTILINE):
            fm_text = re.sub(
                r"^metadata:.*$",
                f'metadata:\n  version: "{version}"',
                fm_text, flags=re.MULTILINE,
            )
        else:
            fm_text = fm_text.rstrip() + f'\nmetadata:\n  version: "{version}"\n'
        changed.append("version")

    if description:
        if re.search(r"^description:.*$", fm_text, re.MULTILINE):
            # substitui a linha description: e o bloco seguinte até a próxima chave
            fm_text = re.sub(
                r"^description:.*?(?=^\w+:|\Z)",
                f"description: >\n  {description.strip()}\n",
                fm_text, flags=re.MULTILINE | re.DOTALL,
            )
        else:
            fm_text = fm_text.rstrip() + f"\ndescription: >\n  {description.strip()}\n"
        changed.append("description")

    if not changed:
        return {"ok": False, "error": "Nada a atualizar (informe version ou description)."}

    new_content = "---" + fm_text + "---" + body
    skill_md.write_text(new_content, encoding="utf-8")
    return {"ok": True, "skill": name, "changed": changed}


# --------------------------------------------------------------------------
# Definição das ferramentas MCP
# --------------------------------------------------------------------------

TOOLS = [
    {
        "name": "create_skill",
        "description": (
            "Cria a estrutura completa de uma skill nova (SKILL.md + scripts/ + references/ + "
            "assets/ + tests/). Use quando o usuário quiser criar uma skill. "
            "PT: criar skill, nova skill, gerar skill. EN: create skill, new skill, scaffold skill."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nome da skill ([a-z][a-z0-9_-]*)"},
                "description": {"type": "string", "description": "Descrição de ativação (25+ palavras)"},
                "with_tests": {"type": "boolean", "description": "Criar pasta tests/ com tabela de casos", "default": True},
                "force": {"type": "boolean", "description": "Sobrescrever se já existir", "default": False},
            },
            "required": ["name", "description"],
        },
    },
    {
        "name": "validate_skill",
        "description": (
            "Valida uma skill: frontmatter, seções obrigatórias, referências a arquivos, "
            "tamanho do corpo e casos de teste. Use após criar/editar uma skill. "
            "PT: validar skill, verificar skill, checar skill. EN: validate skill, lint skill."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nome da skill"},
                "strict": {"type": "boolean", "description": "Trata avisos como erros", "default": False},
            },
            "required": ["name"],
        },
    },
    {
        "name": "test_skill",
        "description": (
            "Executa os testes declarados em tests/test-cases.json de uma skill. "
            "PT: testar skill, rodar testes. EN: test skill, run skill tests."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Nome da skill"}},
            "required": ["name"],
        },
    },
    {
        "name": "list_skills",
        "description": (
            "Lista todas as skills instaladas com versão e recursos. "
            "PT: listar skills, quais skills existem. EN: list skills, show skills."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_skill",
        "description": (
            "Lê o conteúdo do SKILL.md de uma skill. Use para revisar ou melhorar uma skill. "
            "PT: ler skill, ver skill. EN: read skill, view skill."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nome da skill"},
                "max_chars": {"type": "integer", "description": "Limite de caracteres", "default": 20000},
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_skill_template",
        "description": (
            "Devolve o template anotado de SKILL.md com explicações de cada seção. "
            "PT: template de skill, modelo de skill. EN: skill template."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "update_skill",
        "description": (
            "Atualiza o frontmatter de uma skill (version e/ou description) sem tocar no corpo. "
            "PT: atualizar skill, mudar versão da skill. EN: update skill, bump version."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nome da skill"},
                "version": {"type": "string", "description": "Nova versão (semver)"},
                "description": {"type": "string", "description": "Nova descrição de ativação"},
            },
            "required": ["name"],
        },
    },
]

DISPATCH = {
    "create_skill": lambda a: create_skill(
        a["name"], a.get("description", ""),
        with_tests=a.get("with_tests", True), force=a.get("force", False),
    ),
    "validate_skill": lambda a: validate_skill(a["name"], a.get("strict", False)),
    "test_skill": lambda a: test_skill(a["name"]),
    "list_skills": lambda a: list_skills(),
    "read_skill": lambda a: read_skill(a["name"], a.get("max_chars", 20000)),
    "get_skill_template": lambda a: get_skill_template(),
    "update_skill": lambda a: update_skill(a["name"], a.get("version"), a.get("description")),
}


# --------------------------------------------------------------------------
# Camada JSON-RPC / MCP
# --------------------------------------------------------------------------

def _text_result(payload, is_error: bool = False) -> dict:
    return {
        "content": [{"type": "text", "text": json.dumps(payload, indent=2, ensure_ascii=False)}],
        "isError": is_error,
    }


def handle_request(request: dict):
    method = request.get("method", "")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }

    if method in ("notifications/initialized", "notifications/cancelled"):
        return None

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = request.get("params", {}) or {}
        tool_name = params.get("name", "")
        args = params.get("arguments", {}) or {}

        handler = DISPATCH.get(tool_name)
        if handler is None:
            return {
                "jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32602, "message": f"Ferramenta desconhecida: {tool_name}"},
            }

        try:
            result = handler(args)
        except KeyError as exc:
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": _text_result({"ok": False, "error": f"argumento ausente: {exc}"}, is_error=True),
            }
        except Exception as exc:  # pragma: no cover
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": _text_result({"ok": False, "error": f"erro interno: {exc}"}, is_error=True),
            }

        is_error = isinstance(result, dict) and result.get("ok") is False
        return {"jsonrpc": "2.0", "id": req_id, "result": _text_result(result, is_error=is_error)}

    return {
        "jsonrpc": "2.0", "id": req_id,
        "error": {"code": -32601, "message": f"Método desconhecido: {method}"},
    }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps({
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }), flush=True)
            continue

        try:
            response = handle_request(request)
        except Exception as exc:  # pragma: no cover
            response = {
                "jsonrpc": "2.0", "id": request.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {exc}"},
            }

        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)

    sys.stdin.close()


if __name__ == "__main__":
    main()