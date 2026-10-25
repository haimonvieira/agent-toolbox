# Padrões de Integração Skill + MCP

## Visão Geral

Uma skill e um servidor MCP são complementos, não alternativas. A divisão de
responsabilidades é rígida:

| Responsabilidade | Skill | Servidor MCP |
|---|---|---|
| Decisão de fluxo | ✅ | ❌ |
| Dados em tempo real | ❌ | ✅ |
| Autenticação | ❌ (nunca armazene credenciais) | ✅ |
| Autorização | ❌ | ✅ |
| Sequência de chamadas | ✅ | ❌ |
| Retry / degrade | ✅ (orquestra) | ❌ (executa) |
| Formato de saída | ✅ | ❌ (retorna JSON cru) |
| Ações controladas | ❌ (decide) | ✅ (executa e protege) |

---

## Padrão A — Leitura (Skill Consome MCP)

```
┌──────────────┐     1. decide chamar     ┌──────────────┐
│              │ ────────────────────────▶ │              │
│    SKILL     │                           │  MCP SERVER  │
│  (decisão,   │     2. retorna dados      │  (dados,     │
│   formato)   │ ◀──────────────────────── │   auth)      │
│              │                           │              │
└──────────────┘     3. analisa, formata   └──────────────┘
                     e entrega ao usuário
```

**Casos típicos**: relatórios, análise de dados, briefings, diagnósticos.

**Quando usar**: a skill precisa de dados externos, mas não precisa modificar estado.

**Exemplo**: `customer-briefing`
```
1. Skill valida entrada (cliente, período)
2. Skill chama get_account_activity(customer_id, period)
3. Skill analisa os dados, detecta anomalias
4. Skill formata relatório conforme assets/briefing-template.md
5. Skill entrega
```

**Regras**:
- A skill deve validar a resposta do MCP antes de usar.
- Dados ausentes ≠ dados zero. Informe a lacuna.
- Nunca cacheie dados que o MCP pode atualizar.

---

## Padrão B — Escrita com Validação (Skill Orquestra MCP)

```
┌──────────┐  1. read ┌──────────┐  3. write ┌──────────┐
│          │ ────────▶ │          │ ─────────▶ │          │
│  SKILL   │           │  MCP     │            │  MCP     │
│          │ ◀───────  │          │            │          │
│          │  2. dados │  Server  │  4. write  │  Server  │
│          │ ────────▶ │          │ ─────────▶ │ (verif.) │
│          │           │          │            │          │
│          │  5. decide│          │            │          │
│          │   próximo │          │            │          │
└──────────┘           └──────────┘            └──────────┘
```

**Casos típicos**: criação de tickets, aprovação de mudanças, pipelines de ação.

**Quando usar**: a skill precisa ler, decidir, escrever e confirmar.

**Exemplo**: `incident-response`
```
1. Skill chama read_logs(path) → dados
2. Skill analisa: classifica gravidade (decisão da skill)
3. Se gravidade >= ALTA: chama create_jira_issue(prioridade=urgente)
4. Skill verifica: get_issue_status(issue_id) == "created"?
5. Se confirmado: notifica. Se não: retry ou alerta manual.
6. Skill gera post de Slack (assets/slack-template.md)
```

**Regras de escrita**:
- Sempre verifique que a ação foi executada (step 4).
- Ações irreversíveis precisam de confirmação explícita do usuário,
  a menos que a política diga o contrário.
- Cada ação deve ter um `idempotency_key` quando o MCP suportar.

---

## Padrão C — Fallback / Degradacão

Quando o servidor MCP está indisponível:

```
┌──────────┐  tenta MCP
│          │ ──────────❌ falha
│  SKILL   │           │
│          │  ┌────────┴────────┐
│          │  │ 1. retry (3x)   │
│          │  │ 2. cache/local  │
│          │  │ 3. modo parcial │
│          │  │ 4. informa      │
└──────────┘  └────────────────┘
```

**Estratégia em camadas**:

| Camada | Ação | Custo |
|---|---|---|
| Retry | 3 tentativas, backoff 2s/4s/8s | Baixo |
| Cache | Use `references/fallback-data.md` se existir | Médio |
| Modo parcial | Gere o que for possível, marque dados ausentes | Médio |
| Recusa informada | Diga claramente o que não funcionou | Baixo (mas frustra) |

**Regra**: nunca silencie uma falha de MCP. O usuário deve saber quais partes
do resultado vêm de dados reais e quais são inferências ou ausências.

---

## Padrão D — Skill que Seleciona Ferramenta MCP

Quando um servidor MCP expõe muitas ferramentas e a skill precisa escolher:

```
SKILL → [decide qual ferramenta] → MCP Tool A ou B ou C
```

**Regras**:
- Se o MCP tem 5+ ferramentas, a skill deve ter uma **regra de seleção** explícita.
- A regra deve ser baseada em: tipo de entrada, urgência, recurso acessado.
- Documente a regra no corpo da skill em forma de tabela.

**Exemplo** (ferramentas de suporte):
| Entrada | Ferramenta | Porquê |
|---|---|---|
| "bug", "erro", "falha" | `create_bug_issue` | Rastreabilidade técnica |
| "dúvida", "como fazer" | `create_kb_article` | Base de conhecimento |
| "reembolso", "devolver" | `process_refund` | Fluxo financeiro |

---

## Autenticação

A skill **nunca** deve:
- Armazenar chaves de API ou tokens.
- Pedir ao usuário que cole credenciais no chat.
- Incluir auth em URLs ou cabeçalhos manualmente.

O servidor MCP lida com auth. A skill apenas:
- Informa ao usuário quando a auth expirou (`401 Unauthorized`).
- Sabe qual tipo de auth é necessário para declarar a dependência.

**Padrões comuns**:

| Tipo | Quando usar | Papel da skill |
|---|---|---|
| API key via env | Serviços internos, simples | Nenhum — o MCP lê a variável |
| OAuth 2.1 | Serviços ao usuário (Google, GitHub) | Redireciona para auth flow do MCP |
| Sem auth | Dados públicos | Nenhum |
| JWT interno | Microserviços | Nenhum |

---

## Declaração de Dependências

### OpenAI (`agents/openai.yaml`)

```yaml
dependencies:
  tools:
    - type: "mcp"
      value: "customer-data"
      description: "Dados de atividade e metadados do cliente"
      transport: "streamable_http"
      url: "https://mcp.example.com/api/mcp"
    - type: "mcp"
      value: "jira"
      description: "Criação e acompanhamento de issues"
      transport: "stdio"
      command: "npx"
      args: ["-y", "@smithery/cli@latest", "run", "jira", "--client", "claude"]
```

### Claude Desktop (`claude_desktop.config.json`)

```json
{
  "mcpServers": {
    "customer-data": {
      "command": "npx",
      "args": ["-y", "@smithery/cli@latest", "run", "customer-data", "--client", "claude"]
    }
  }
}
```

### Genérico (variável de ambiente)

A skill deve declarar qual variável o servidor espera:
```
customer-data necessita CUSTOMER_DATA_API_KEY
```

---

## Checklist de Integração

- [ ] Skill não armazena credenciais
- [ ] Servidor MCP está declarado na dependência
- [ ] Tipo de transport (stdio / streamable-http / sse) está definido
- [ ] Tabela de erros e tratamentos existe
- [ ] Retry com backoff está definido (máx 3 tentativas)
- [ ] Ações irreversíveis têm confirmação ou política explícita
- [ ] Ações têm verificação de confirmação (read-after-write)
- [ ] Degradação está definida para falha de MCP
- [ ] Skill não tenta contornar auth
- [ ] Ferramentas MCP escolhidas têm justificação na skill