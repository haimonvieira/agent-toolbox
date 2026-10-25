# Harness de Avaliação (Camada Avançada)

A skill-creator inclui um harness de avaliação de duas trilhas. A **Trilha A**
sempre funciona neste ambiente; a **Trilha B** é a ferramenta de nível de
desenvolvedor do skill-creator oficial (Anthropic) e exige o Claude Code CLI.

---

## Trilha A — Nativa Minis (sempre disponível)

Ferramentas determinísticas, sem LLM, sem rede.

| Ferramenta | O que faz | Dependência |
|---|---|---|
| `scripts/skill-validate.py` | Valida frontmatter, seções, referências, casos de teste, spec Claude | nenhuma |
| `scripts/skill-test.py` | Executa `tests/test-cases.json` | nenhuma |
| `scripts/skill-scaffold.sh` | Gera a estrutura inicial | nenhuma |
| `scripts/quick_validate.py` | Valida só o frontmatter contra a **spec do Claude** | PyYAML |
| `scripts/package_skill.py` | Empacota a skill em `.skill` (zip) | PyYAML |
| `mcp/skill-server.py` | Servidor MCP com 7 ferramentas | nenhuma |

```bash
# validação completa (spec Minis + avisos da spec Claude)
python3 scripts/skill-validate.py /var/minis/skills/<nome> --strict --json

# testes
python3 scripts/skill-test.py /var/minis/skills/<nome>

# conformidade estrita com a spec do Claude
python3 scripts/quick_validate.py /var/minis/skills/<nome>

# empacotar
python3 scripts/package_skill.py /var/minis/skills/<nome> ./dist
```

**Quando usar**: sempre. É o piso mínimo — nenhuma skill deve ser declarada
pronta sem passar por aqui.

---

## Trilha B — Avaliação por LLM (requer Claude Code CLI)

O skill-creator oficial traz um loop que **mede se a descrição da skill dispara
corretamente** usando um modelo, e depois **reescreve a descrição** até atingir
a taxa de acerto desejada.

| Arquivo | Papel |
|---|---|
| `scripts/run_eval.py` | Roda `claude -p` para cada prompt de avaliação e mede se a skill disparou |
| `scripts/run_loop.py` | Repete eval → melhora descrição → eval, até passar ou atingir o máximo |
| `scripts/improve_description.py` | Reescreve a descrição com base nos falsos positivos/negativos |
| `scripts/aggregate_benchmark.py` | Agrega resultados de benchmark em métricas |
| `scripts/generate_report.py` | Gera relatório HTML comparativo |
| `agents/analyzer.md` | Prompt do agente analisador (falhas de ativação) |
| `agents/comparator.md` | Prompt do agente comparador (A/B de descrições) |
| `agents/grader.md` | Prompt do agente avaliador (nota de qualidade) |
| `eval-viewer/` | Visualizador HTML dos resultados |
| `references/schemas.md` | Schemas JSON de `evals/evals.json` e dos relatórios |

### Formato do conjunto de avaliação

Cada skill avaliada define `evals/evals.json`:

```json
{
  "skill_name": "minha-skill",
  "evals": [
    {"id": 1, "prompt": "Gere um briefing do cliente Acme", "should_trigger": true},
    {"id": 2, "prompt": "Explique o que é um ORM", "should_trigger": false}
  ]
}
```

Cada entrada marca `should_trigger` — o teste verifica se a skill **dispara
quando deve** e **não dispara quando não deve**. É a medição objetiva da
qualidade da descrição.

### Pré-requisito

```bash
which claude      # precisa do Claude Code CLI instalado e autenticado
```

**Neste ambiente o `claude` CLI não está instalado** → a Trilha B não roda.
Use a Trilha A + os 5 casos de teste manuais como substituto.

**Substituto manual**: para cada prompt do conjunto, verifique se a skill
dispara e se o resultado é correto. Registre na tabela de casos de teste do
`SKILL.md`.

---

## Como as duas trilhas se combinam

```
1. Criar skill             → skill-scaffold.sh ou MCP create_skill
2. Validar estrutura       → skill-validate.py --strict     [Trilha A]
3. Testar scripts          → skill-test.py                  [Trilha A]
4. Checar spec Claude      → quick_validate.py              [Trilha A]
5. (Opcional) Medir ativação com LLM → run_eval.py/run_loop.py  [Trilha B]
6. Empacotar               → package_skill.py               [Trilha A]
```

Se a Trilha B estiver disponível, ela substitui o passo 5 e é o padrão-ouro:
mede a ativação objetivamente em vez de você julgar manualmente.

---

## Referência rápida — limites da spec do Claude

Enforçados por `quick_validate.py`:

| Campo | Regra |
|---|---|
| Chaves permitidas | `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility` |
| `name` | kebab-case `[a-z0-9-]`, sem hífen no início/fim, sem `--`, ≤ 64 chars |
| `description` | string, sem `<` ou `>`, ≤ 1024 chars |
| `compatibility` | string, ≤ 500 chars |
| Versão | **não é chave de topo** — use `metadata.version` |

> **Nota Minis**: skills deste ambiente podem usar `version:` no topo (convenção
> herdada). Para distribuição no Claude, mova para `metadata.version`. O
> `skill-validate.py` aceita ambos e avisa quando a chave extra está presente.