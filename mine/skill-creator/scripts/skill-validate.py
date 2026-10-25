#!/usr/bin/env python3
"""
skill-validate.py — Valida a estrutura e integridade de uma skill.

Verifica:
  1. SKILL.md existe e é legível
  2. Frontmatter: name (obrigatório), description (obrigatório), version
  3. Seções obrigatórias e recomendadas do corpo
  4. Referências a scripts/references/assets citados existem no disco
     (inclui busca em outras skills, para referências cruzadas)
  5. Tamanho do corpo (alerta se > 500 linhas)
  6. Descrição vaga ou curta demais
  7. Casos de teste presentes

Uso:
  python3 skill-validate.py <caminho-da-skill> [--strict] [--json]

Variáveis de ambiente:
  SKILLS_ROOT          diretório raiz das skills (padrão: ~/.agent-skills)
  IGNORE_EXTERNAL_REF  se "true", não verifica referências cruzadas

Exit codes:
  0  = aprovado (podem existir avisos)
  1  = reprovado (erros críticos)
  2  = uso incorreto
"""

import json
import os
import re
import sys
from pathlib import Path

SKILLS_ROOT = Path(os.environ.get("SKILLS_ROOT", Path.home() / ".agent-skills"))
IGNORE_EXTERNAL_REF = os.environ.get("IGNORE_EXTERNAL_REF", "").lower() in ("1", "true", "yes", "on")

REQUIRED_FRONTMATTER = ["name", "description"]
OPTIONAL_FRONTMATTER = ["compatibility"]

# Cada seção aceita equivalentes em PT e EN (case-insensitive).
# Seções ausentes geram AVISO (não erro): são guia estrutural, não requisito rígido.
# O gate rígido é o quick_validate.py (spec do Claude).
CORE_SECTIONS = [
    ("Quando usar", "when to use", "quando usar", "when to use this skill"),
    ("Fronteira do fluxo", "workflow boundary", "the workflow", "fronteira do fluxo"),
    ("Critérios de sucesso", "success criteria", "critérios de sucesso"),
    ("Casos de teste", "test cases", "casos de teste", "testing"),
]
RECOMMENDED_SECTIONS = [
    ("Integração MCP", "mcp integration", "integração mcp"),
    ("Recursos auxiliares", "supporting resources", "bundled resources",
     "recursos auxiliares", "resources"),
    ("Proibições", "prohibitions", "constraints", "don't", "do not",
     "limitations", "proibições"),
    ("Pontos de parada", "stop points", "stop conditions", "pontos de parada"),
]

VAGUE_PATTERNS = [
    r"\bajuda\s+a\s*\b",
    r"\bpermite\s+",
    r"\bútil\s+para\b",
    r"\bdiversas\s+tarefas\b",
    r"\bmuitos\s+usos\b",
    r"\bajuda\s+com\b",
]

MIN_DESCRIPTION_WORDS = 25


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.infos = []

    def add_error(self, msg):
        self.errors.append(msg)

    def add_warning(self, msg):
        self.warnings.append(msg)

    def add_info(self, msg):
        self.infos.append(msg)

    @property
    def passed(self):
        return not self.errors

    def to_dict(self):
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "infos": self.infos,
        }


def parse_frontmatter(content: str) -> tuple:
    """Extrai frontmatter YAML (blocos > e | e um nível de aninhamento) e o corpo.
    Retorna (dict, corpo). Valores aninhados viram dicts."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    fm_text = parts[1]
    body = parts[2].strip()

    fm = {}
    block_key = None
    block_lines = []
    nested_key = None
    nested = {}

    def flush_block():
        nonlocal block_key, block_lines
        if block_key is not None:
            fm[block_key] = "\n".join(block_lines).strip()
        block_key = None
        block_lines = []

    def flush_nested():
        nonlocal nested_key, nested
        if nested_key is not None:
            fm[nested_key] = dict(nested)
        nested_key = None
        nested = {}

    for raw in fm_text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        indented = line.startswith((" ", "\t"))
        if not indented and ":" in line:
            flush_block()
            flush_nested()
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value in (">", "|", ">-", "|-", ">+", "|+"):
                block_key = key
                block_lines = []
            elif value == "":
                nested_key = key
                nested = {}
            else:
                fm[key] = value.strip().strip('"').strip("'")
        else:
            if block_key is not None:
                block_lines.append(line.strip())
            elif nested_key is not None and ":" in line:
                k, _, v = line.partition(":")
                nested[k.strip()] = v.strip().strip('"').strip("'")

    flush_block()
    flush_nested()
    return fm, body


def get_version(fm: dict) -> str:
    """Versão pode estar no topo (convenção de alguns clientes) ou em metadata.version (spec Claude)."""
    if fm.get("version"):
        return str(fm["version"])
    meta = fm.get("metadata")
    if isinstance(meta, dict) and meta.get("version"):
        return str(meta["version"])
    return ""


CLAUDE_ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def check_frontmatter(fm: dict, r: ValidationResult):
    for field in REQUIRED_FRONTMATTER:
        if field not in fm or not fm[field]:
            r.add_error(f"Campo obrigatório '{field}' ausente no frontmatter.")

    name = fm.get("name", "")
    if name:
        if not re.match(r"^[a-z][a-z0-9_-]*$", name):
            r.add_error(
                f"Nome '{name}' inválido. Use letras minúsculas, números, "
                "hífen ou underscore, começando por letra."
            )
        elif "_" in name:
            r.add_warning(
                f"Nome '{name}' usa underscore — a spec do Claude exige kebab-case "
                "(apenas [a-z0-9-]). Prefira hífen para portabilidade."
            )
        if len(name) > 64:
            r.add_warning(f"Nome com {len(name)} caracteres (máx spec: 64).")

    desc = fm.get("description", "")
    if desc:
        words = len(desc.split())
        if words < MIN_DESCRIPTION_WORDS:
            r.add_warning(
                f"Descrição com {words} palavras (recomendado: {MIN_DESCRIPTION_WORDS}+). "
                "Descrições robustas cobrem ativação direta, indireta e condições de exclusão."
            )
        if "<" in desc or ">" in desc:
            r.add_warning("Descrição contém '<' ou '>' — proibido pela spec do Claude.")
        if len(desc) > 1024:
            r.add_warning(f"Descrição com {len(desc)} caracteres (máx spec: 1024).")
        for pat in VAGUE_PATTERNS:
            m = re.search(pat, desc, re.IGNORECASE)
            if m:
                r.add_warning(
                    f"Descrição usa linguagem vaga ('{m.group(0).strip()}'). "
                    "Seja específico sobre o objetivo do usuário."
                )

    compat = fm.get("compatibility", "")
    if compat and isinstance(compat, str) and len(compat) > 500:
        r.add_warning(f"'compatibility' com {len(compat)} caracteres (máx spec: 500).")

    # Chaves fora da spec do Claude (avisos, pois alguns clientes aceitam extensões)
    extras = set(fm.keys()) - CLAUDE_ALLOWED_KEYS
    for extra in sorted(extras):
        r.add_warning(
            f"Chave '{extra}' não pertence à spec do Claude "
            f"({', '.join(sorted(CLAUDE_ALLOWED_KEYS))}). "
            "Para distribuição no Claude, mova para 'metadata'."
        )

    if not get_version(fm):
        r.add_info("Versão não declarada. Use 'metadata: {version: \"x.y.z\"}' (spec Claude) "
                   "ou 'version:' no topo (convenção de alguns clientes).")

    for field in OPTIONAL_FRONTMATTER:
        if field not in fm:
            r.add_info(f"Campo opcional '{field}' não definido.")


def resolve_reference(fname: str, folder: str, skill_dir: Path) -> bool:
    """Verifica se uma referência existe na skill ou em outra skill."""
    if fname.endswith("/"):
        return True
    local = skill_dir / folder.rstrip("/") / fname
    if local.exists():
        return True
    if IGNORE_EXTERNAL_REF:
        return True
    if SKILLS_ROOT.is_dir():
        for other in SKILLS_ROOT.iterdir():
            if other.is_dir() and (other / folder.rstrip("/") / fname).exists():
                return True
    return False


def strip_code_blocks(text: str) -> str:
    """Remove blocos de código cercados (```...```) para não confundir
    templates embutidos com seções reais."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def check_body(body: str, skill_dir: Path, r: ValidationResult):
    body_for_sections = strip_code_blocks(body)
    lines = body.splitlines()
    if len(lines) > 500:
        r.add_warning(
            f"Corpo com {len(lines)} linhas (limite recomendado: 500). "
            "Mova conteúdo detalhado para references/."
        )

    def has_section(alternatives):
        """Procura um heading H2 cujo texto case com qualquer alternativa (PT/EN)."""
        headings = re.findall(r"^#{1,3}[ \t]+(.+?)[ \t]*$", body_for_sections, re.MULTILINE)
        for h in headings:
            low = h.strip().strip("*`_ ").lower()
            for alt in alternatives:
                if alt.lower() in low:
                    return True
        return False

    for alts in CORE_SECTIONS:
        if not has_section(alts):
            r.add_warning(f"Seção estrutural '{alts[0]}' (ou '{alts[1]}') ausente.")
            break  # um aviso agregado evita ruído quando a skill não segue o template

    missing_rec = [alts[0] for alts in RECOMMENDED_SECTIONS if not has_section(alts)]
    if len(missing_rec) == len(RECOMMENDED_SECTIONS):
        r.add_warning(
            "Skill não segue o template estrutural (sem seções de fluxo/proibições/recursos). "
            "Aceitável em skills simples; veja references/skill-template.md."
        )
    elif missing_rec:
        r.add_warning(f"Seções recomendadas ausentes: {', '.join(missing_rec)}.")

    if not re.search(r"\bn[ãa]o\b", body_for_sections, re.IGNORECASE):
        r.add_warning(
            "Nenhuma proibição explícita ('NÃO ...') encontrada. "
            "Skills fortes dizem ao modelo o que NÃO fazer."
        )

    # Referências a arquivos (apenas caminhos com extensão real)
    for folder in ["scripts/", "references/", "assets/"]:
        ref_re = re.compile(
            rf"{re.escape(folder)}([A-Za-z0-9_][A-Za-z0-9_.\-/]*\.[A-Za-z0-9]+)"
        )
        for fname in ref_re.findall(body_for_sections):
            if not resolve_reference(fname, folder, skill_dir):
                r.add_warning(
                    f"Arquivo referenciado '{folder}{fname}' não encontrado no disco."
                )

    # Casos de teste (considera a ÚLTIMA ocorrência da seção, que é a real)
    if "## Casos de teste" in body_for_sections:
        idx = body_for_sections.rfind("## Casos de teste")
        section = body_for_sections[idx:idx + 3000]
        if "|" not in section:
            r.add_warning("Seção 'Casos de teste' parece vazia (sem tabela).")
        else:
            for tipo in ["Direto", "Indireto", "Incompleto", "Negativo", "Borda"]:
                if tipo not in section:
                    r.add_warning(f"Caso de teste '{tipo}' ausente na tabela.")


def check_structure(skill_dir: Path, r: ValidationResult):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        r.add_error("SKILL.md não encontrado.")
        return

    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        r.add_error(f"Não foi possível ler SKILL.md: {exc}")
        return

    fm, body = parse_frontmatter(content)
    check_frontmatter(fm, r)
    check_body(body, skill_dir, r)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    as_json = "--json" in sys.argv

    if not args:
        print("Uso: skill-validate.py <caminho-da-skill> [--strict] [--json]", file=sys.stderr)
        sys.exit(2)

    skill_dir = Path(args[0]).resolve()
    if not skill_dir.is_dir():
        print(f"ERRO: '{skill_dir}' não é um diretório.", file=sys.stderr)
        sys.exit(2)

    result = ValidationResult()
    check_structure(skill_dir, result)

    if strict and result.warnings:
        result.errors.extend([f"[strict] {w}" for w in result.warnings])
        result.warnings = []

    if as_json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        status = "✅ APROVADO" if result.passed else "❌ REPROVADO"
        print(f"Skill: {skill_dir.name}")
        print(f"Status: {status}")
        if result.errors:
            print(f"\nErros ({len(result.errors)}):")
            for e in result.errors:
                print(f"  ✗ {e}")
        if result.warnings:
            print(f"\nAvisos ({len(result.warnings)}):")
            for w in result.warnings:
                print(f"  ⚠ {w}")
        if result.infos:
            print(f"\nInformações ({len(result.infos)}):")
            for i in result.infos:
                print(f"  ℹ {i}")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()