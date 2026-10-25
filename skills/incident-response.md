# incident-response

## Descrição declarada

Diagnostica incidentes de producao a partir de logs e gera plano de acao com post de Slack, checklist e ticket de tracking. Use quando o usuario colar logs de erro, pedir para analisar incidente, diagnosticar falha, "o que quebrou", "analise de incidente", "pos-mortem", "o que aconteceu com o sistema", "deu erro na producao", "investigar falha", ou enviar trecho de log e pedir interpretacao. Tambem ativa se o usuario pedir "gerar comunicado de incidente", "plano de acao", "checklist do que fazer", ou mencionar spike de erro, 5xx, timeout, exception. Nao use para requests de feature, duvidas de negocio, ou logs sem mensagem de erro. Suporta modo com servidor MCP (cria ticket no Jira) e modo apenas-skill (analise + comunicado). Scripts necessarios: scripts/parse_logs.py.

## Origem

| Campo | Valor |
|---|---|
| Repositório | local |
| Caminho | `skills/incident-response/` |
| Licença | MIT |
| Confiança | confirmado |

Autoral.

## Recursos

`scripts/`, `references/`, `assets/`, `tests/`

## Tamanho

- `SKILL.md`: 6,778 bytes, 125 linhas de corpo
- Arquivos no diretório: 5
- Versão declarada: 1.0.0
