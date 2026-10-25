#!/bin/sh
# skill-scaffold.sh — Gera a estrutura de uma skill nova.
# Uso: skill-scaffold.sh <nome-da-skill> [descrição opcional]
# Exemplo: ./skill-scaffold.sh customer-briefing "Gera relatórios de briefing..."

set -e

SKILLS_DIR="${SKILLS_DIR:-.}"
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_REF="${SKILL_TEMPLATE:-$SELF_DIR/../references/skill-template.md}"

if [ $# -lt 1 ]; then
    echo "Uso: $0 <nome-da-skill> [descricao]"
    echo "Variaveis de ambiente: SKILLS_DIR (padrao: diretorio atual), SKILL_TEMPLATE"
    exit 64
fi

NAME="$1"
DIR="${SKILLS_DIR}/${NAME}"

if [ -d "$DIR" ]; then
    echo "ERRO: o diretório '$DIR' já existe."
    exit 1
fi

# Validação do nome (snake/kebab case)
case "$NAME" in
    *[!a-z0-9_-]*) 
        echo "ERRO: o nome deve conter apenas letras minúsculos, números, hífen e underscore (ex: minha-skill, minha_skill)."
        exit 64
        ;;
esac

mkdir -p "$DIR/scripts" "$DIR/references" "$DIR/assets"

# --- SKILL.md com frontmatter interpolado ---
cat > "$DIR/SKILL.md" <<SKILLEOF
---
name: ${NAME}
description: >
  ${2:-Descreva aqui o objetivo da skill e quando ela deve ser ativada.
  Inclua variacoes de linguagem do usuario e condicoes de ativacao.
  Este campo e o mecanismo principal de ativacao — seja exaustivo.}
metadata:
  version: "1.0.0"
---

# ${NAME}

## Quando usar

### Gatilhos
-

### Não usar
-

## Fronteira do fluxo

### Entrada
-

### Passos
1.
2.
3.

### Saída
-

### Proibições
- NÃO

### Pontos de parada
- PERGUNTE se
- RECUSE se

## Integração MCP

### Servidores necessários
| Servidor | Ferramenta | Propósito | Auth |
|---|---|---|---|
| | | | |

### Declaração de dependência
\`\`\`yaml
dependencies:
  tools:
    - type: "mcp"
      value: ""
      description: ""
      transport: "streamable_http"
      url: ""
\`\`\`

### Tratamento de erro
| Situação | Ação |
|---|---|
| | |

## Recursos auxiliares
- \`references/\` — consulte quando:
- \`scripts/\` — execute quando:
- \`assets/\` — use como template para:

## Critérios de sucesso
-

## Casos de teste
| # | Tipo | Entrada | Comportamento esperado |
|---|---|---|---|
| 1 | Direto | | |
| 2 | Indireto | | |
| 3 | Incompleto | | |
| 4 | Negativo | | |
| 5 | Borda | | |
SKILLEOF

# --- Arquivos auxiliares (placeholders) ---
: > "$DIR/.gitkeep"
: > "$DIR/scripts/.gitkeep"
: > "$DIR/references/.gitkeep"
: > "$DIR/assets/.gitkeep"

echo "Skill criada em: $DIR"
echo "  SKILL.md        — frontmatter + corpo (preencha)"
echo "  scripts/        — código determinístico"
echo "  references/     — políticas, schemas, exemplos"
echo "  assets/         — templates de saída"
echo ""
echo "Próximos passos:"
echo "  1. Preencha a descricao no frontmatter (é o gatilho principal)"
echo "  2. Defina os passos do fluxo e as proibicoes"
echo "  3. Adicione recursos em scripts/ references/ assets/"
echo "  4. Execute os 5 cenarios de teste"
echo "  5. Valide com: ./skill-validate.py $DIR"
exit 0