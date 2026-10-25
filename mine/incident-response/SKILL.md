---
name: incident-response
description: >
  Diagnostica incidentes de producao a partir de logs e gera plano de acao com post de Slack,
  checklist e ticket de tracking. Use quando o usuario colar logs de erro, pedir para analisar
  incidente, diagnosticar falha, "o que quebrou", "analise de incidente", "pos-mortem",
  "o que aconteceu com o sistema", "deu erro na producao", "investigar falha",
  ou enviar trecho de log e pedir interpretacao.
  Tambem ativa se o usuario pedir "gerar comunicado de incidente", "plano de acao",
  "checklist do que fazer", ou mencionar spike de erro, 5xx, timeout, exception.
  Nao use para requests de feature, duvidas de negocio, ou logs sem mensagem de erro.
  Suporta modo com servidor MCP (cria ticket no Jira) e modo apenas-skill (analise + comunicado).
  Scripts necessarios: scripts/parse_logs.py.
compatibility: python3; jira-mcp (opcional)
metadata:
  version: "1.0.0"
---

# Incident Response

## Quando usar

### Gatilhos
- O usuário cole ou anexe logs com ERROR, FATAL, Exception, Traceback
- O usuário mencione: "incidente", "falha", "quebrou", "5xx", "spike de erro", "produção caída"
- O usuário peça: "analise o que aconteceu", "diagnostique", "gerar comunicado", "plano de ação"
- O usuário envie um trecho de log e pergunte "o que isso significa?"
- O usuário mencione on-call, pager, deploy ruim, rollback

### Não usar
- Logs apenas de acesso (INFO, DEBUG) sem erro — use `log-review-skill`
- Requests de feature ou planejamento — use `planning-skill`
- Dados de negócios (vendas, métricas de revenue) — use `analytics-skill`
- Logs de sistema sem contexto de deploy

---

## Fronteira do fluxo

### Entrada
- **Obrigatório**: trecho de log (mínimo 5 linhas) ou caminho para arquivo de log
- **Opcional**: janela de tempo, nome do serviço, histórico de deploys
- Se o log tiver menos de 3 linhas ou nenhum ERROR/FATAL/Exception: **pergunta** antes de prosseguir
- Valide que o log parece genuíno (não aceite texto genérico como "deu erro")

### Passos
1. Valide a entrada. Se faltar log ou for insuficiente, PERGUNTE. Não invente contexto.
2. Execute `scripts/parse_logs.py` passando o log como stdin. Saída: JSON estruturado com erros, timestamps, frequência.
3. Analise o resultado do script:
   - Identifique o erro raiz (o mais antigo que precede os demais em cascata)
   - Classifique a gravidade: CRÍTICA (dados/perda), ALTA (funcionalidade indisponível), MÉDIA (degradação), BAIXA (warning)
   - Verifique se há padrão conhecido em `references/common-errors.md`
4. Se a gravidade for CRÍTICA ou ALTA e o servidor JIRA MCP estiver configurado:
   - Chame `create_jira_issue` com prioridade correspondente
   - Verifique com `get_issue_status` que foi criado
   - Se falhar, informe mas não bloqueie o restante do fluxo
5. Gere o post de Slack usando `assets/slack-post-template.md`, preenchendo com os dados analisados
6. Gere o checklist de ação (5-7 itens baseados no erro raiz)
7. Adicione nível de confiança (0-100%) baseado na completude do log
8. Entregue: diagnóstico + post Slack + checklist + (opcional) ticket

### Saída
1. **Diagnóstico** (H2): erro raiz, causa provável, serviços afetados, janela de tempo
2. **Gravidade** e **Nível de confiança**
3. **Post de Slack** (bloco de código, copy-paste pronto)
4. **Checklist de ação** (lista numerada)
5. **Ticket JIRA** (se criado: link; se não: motivo)

### Proibições
- NÃO invente nomes de serviços, timestamps ou códigos de erro que não estejam no log
- NÃO classifique como CRÍTICA sem evidência de perda de dados ou indisponibilidade total
- NÃO omita o nível de confiança — se o log for parcial, diga explicitamente
- NÃO crie ticket JIRA sem confirmação do usuário quando a gravidade for BAIXA ou MÉDIA
- NÃO sugera rollback sem evidência de que o deploy é a causa

### Pontos de parada
- PERGUNTE se o log não mostrar janela de tempo clara
- PERGUNTE se houver mais de um erro raiz candidato (peça contexto de deploy)
- RECUSE se o log pertencer a outro cliente (isolamento por tenant) — verifique metadados
- RECUSE se o pedido for para modificar sistema em produção sem aprovação
- DELEGUE para `security-incident` se o erro sugerir ataque (SQL injection, acesso não autorizado)

---

## Integração MCP

### Servidores necessários (opcional)
| Servidor | Ferramenta | Propósito | Auth |
|---|---|---|---|
| jira | create_issue | Criar ticket de incidente | API key via env |
| jira | get_issue_status | Verificar se foi criado | mesma key |

### Declaração de dependência
```yaml
dependencies:
  tools:
    - type: "mcp"
      value: "jira"
      description: "Criacao e acompanhamento de tickets de incidente"
      transport: "streamable_http"
      url: "https://mcp.example.com/api/mcp"
```

### Tratamento de erro
| Situação | Ação |
|---|---|
| `401 Unauthorized` | Informe que auth JIRA expirou — não tente renovar |
| `429 Rate limited` | Retry com backoff 2s/4s/8s (máx 3) |
| Issue creation falha | Siga sem ticket; informe ao usuário no campo dedicado |
| Servidor JIRA offline | Modo skill-only; mencione que ticket não foi criado |
| parse_logs.py falha | Tente análise manual; informe que a análise foi menos precisa |

### Padrão aplicado
**Padrão B (Escrita com Validação)** — skill lê logs, decide gravidade, cria ticket,
verifica criação, e só então comunica. Veja `references/mcp-integration-patterns.md`.

---

## Recursos auxiliares
- `references/common-errors.md` — consulte no passo 3 para identificar padrões conhecidos
- `scripts/parse_logs.py` — execute no passo 2 com o log completo como stdin
- `assets/slack-post-template.md` — use no passo 5 para formatar o comunicado

## Critérios de sucesso
- O diagnóstico menciona apenas erros efetivamente presentes no log
- Nível de confiança está explicitamente declarado (0-100%)
- Post de Slack segue o template (seção: impacto, ação, próximos passos)
- Checklist tem entre 5 e 7 itens acionáveis
- Tempo total: menos de 90 segundos do recebimento do log à entrega
- Se JIRA falhar, o resto do fluxo continua e o usuário é informado

## Casos de teste
| # | Tipo | Entrada | Comportamento esperado |
|---|---|---|---|
| 1 | Direto | "Analise este incidente: <log com ERROR>" | Ativa, gera diagnóstico completo |
| 2 | Indireto | "O que aconteceu com a produção?" + log | Ativa, mesmo resultado |
| 3 | Incompleto | "Analise este incidente" sem log | Pergunta o log |
| 4 | Negativo | "Implemente uma feature de log" | NÃO ativa |
| 5 | Borda | Log com 2 linhas | Informa que é insuficiente |
| 6 | Borda | Log sem ERROR (só INFO) | Recusa ou pede log com erros |
| 7 | Borda | JIRA indisponível | Gera tudo mais, informa falha |