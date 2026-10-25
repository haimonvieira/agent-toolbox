# Template Anotado de Skill

Use este template como ponto de partida. Cada seção tem uma anotação sobre
o que colocar e por quê. As anotações devem ser removidas na versão final.

---

```yaml
---
name: nome-da-skill
# → kebab-case obrigatório: [a-z0-9-], sem hífen no início/fim, sem '--', máx 64 chars.
# → Exemplo: customer-briefing, brand-voice-check, incident-response

description: >
  # → ESTA É A PARTE MAIS IMPORTANTE. O agente só lê isso na fase de descoberta.
  # → Escreva 5–8 frases cobrindo:
  # →   • O objetivo do usuário em linguagem natural
  # →   • Variações de como o usuário pode pedir
  # →   • Condições em que a skill deve ser acionada
  # →   • Condições em que NÃO deve ser acionada
  # →   • Dependências (servidores MCP, ferramentas, scripts)
  # → Limites da spec: sem '<' ou '>', máx 1024 caracteres.
  # → Exemplo:
  # > "Gera relatórios de briefing de cliente a partir de dados de atividade.
  # > Use quando o usuário pedir 'relatório do cliente', 'análise da conta',
  # > 'briefing', 'resumo do cliente', 'atividade recente', 'health check',
  # > ou mencionar revisar a situação de um cliente.
  # > Requer o servidor MCP 'customer-data' com a ferramenta get_account_activity.
  # > Não use para dados em tempo real de sistemas que não tenham servidor MCP."

compatibility: customer-data@^1.0.0, python3
# → Declare servidores MCP (com versão), ferramentas nativas, e requisitos de runtime.
# → Opcional. Máx 500 caracteres.

metadata:
  version: "1.0.0"
  # → Semver. Aumente MAJOR quando mudar a interface (quebra compatibilidade),
  #   MINOR quando adicionar funcionalidade, PATCH quando corrigir bugs.
  # → NOTA: a spec do Claude só permite as chaves name, description, license,
  #   allowed-tools, metadata, compatibility. Por isso a versão fica em metadata.
---
```

```markdown
# Nome da Skill

## Quando usar

### Gatilhos (ativa a skill)
- O usuário menciona: "relatório", "análise", "briefing", "resumo"
- O usuário pede: "me dê um panorama", "como está a conta", "o que aconteceu"
- O usuário faz upload de dados e pede interpretação

### Não usar (desativa)
- O usuário pede dados em tempo real de sistema sem MCP configurado
- O usuário pede apenas dados brutos (use diretamente a ferramenta MCP)
- O usuário quer agendar algo (use outra skill)

→ A lista de "não usar" evita ativações indevidas que gastam contexto.

## Fronteira do fluxo

### Entrada
- O que o fluxo espera: nome do cliente, período (início/fim), opcional: segmento de interesse
- Validação obrigatória: se o período faltar, PERGUNTE antes de prosseguir
- Formatos aceitos: `NdS`, datas ISO, nomes de cliente (verifique com MCP primeiro)

### Passos
1. Valide a entrada. Se faltar dado obrigatório, pergunte. NUNCA invente.
2. Chame `get_account_activity` com `customer_id` e `period`.
3. Se a resposta vier vazia, informe ao usuário — NÃO retorne relatório falso.
4. Execute `scripts/build_briefing.py` com os dados brutos (determinístico).
5. Adicione o contexto de negócio de `references/business-rules.md`.
6. Formate a saída conforme `assets/briefing-template.md`.
7. Se a etapa 2 falhar, tente retry (máx 3, backoff 2s/4s/8s).
8. Se ainda falhar, degrade para modo parcial e informe.

→ Use números. Cada passo deve ter entrada e saída explícitas.
→ Identifique quais passos são scripts (determinísticos) vs decisões do modelo.

### Saída
- Seção 1: Resumo executivo (3 frases)
- Seção 2: Métricas do período em tabela
- Seção 3: Anomalias detectadas (se houver)
- Seção 4: Recomendações de ação
- Formato: markdown com cabeçalhos H2

### Proibições
- NÃO invente métricas que não vieram da ferramenta
- NÃO generalize "tudo bem" se os dados não cobrirem o período completo
- NÃO revele dados de outros clientes (isolamento por tenant)
- NÃO pule a etapa de validação de entrada

### Pontos de parada
- PERGUNTE se o período não for especificado
- PERGUNTE se o cliente não for encontrado no MCP
- RECUSE se o pedido violar política de privacidade (veja `references/compliance.md`)
- DELEGUE para `incident-report` se anomalia indicar falha de sistema

## Integração MCP

### Servidores necessários
| Servidor | Ferramenta | Propósito | Auth |
|---|---|---|---|
| customer-data | get_account_activity | Dados de atividade do cliente | API key via env |
| customer-data | get_customer_meta | Segmento e plano do cliente | mesma key |

### Declaração de dependência (OpenAI `agents/openai.yaml`)
```yaml
dependencies:
  tools:
    - type: "mcp"
      value: "customer-data"
      description: "Dados de atividade e metadados do cliente"
      transport: "streamable_http"
      url: "https://mcp.example.com/api/mcp"
```

### Tratamento de erro
| Situação | Ação |
|---|---|
| `401 Unauthorized` | Informe que a auth expirou — não tente renovar (o servidor cuida) |
| `429 Rate limited` | Retry com backoff exponencial, máx 3 tentativas |
| Resposta vazia | Informe ao usuário; não gere relatório |
| Servidor offline | Degrade para modo parcial; use `references/fallback-data.md` |

## Recursos auxiliares

- `references/compliance.md` — consulte ANTES de gerar qualquer saída com dados de cliente
- `references/business-rules.md` — consulte na etapa 5 para adicionar contexto
- `scripts/build_briefing.py` — execute na etapa 4 com os dados brutos como stdin
- `assets/briefing-template.md` — use como base na etapa 6, preencha lacunas

## Critérios de sucesso

- O relatório contém apenas dados que vieram da ferramenta MCP
- Ausência de dados é explicitamente informada, não mascarada
- O formato segue o template (4 seções, H2)
- Tempo de execução: menos de 90 segundos do pedido à entrega

## Casos de teste

| # | Tipo | Entrada | Comportamento esperado |
|---|---|---|---|
| 1 | Direto | "Gere um briefing do cliente X do último mês" | Ativa, gera relatório completo |
| 2 | Indireto | "Como foi a atividade da Acme em setembro?" | Ativa, mesmo resultado |
| 3 | Incompleto | "Gere um briefing" | Pergunta cliente e período |
| 4 | Negativo | "Agende uma reunião com o cliente X" | NÃO ativa |
| 5 | Borda | Cliente sem atividade no período | Informa vazia, não inventa dados |
```

---

## Principais Padrões de Erro (e como evitar)

| Erro | Sintoma | Correção |
|---|---|---|
| Descrição vaga | Skill não ativa em pedidos indiretos | Liste sinônimos e variações |
| Corpo muito longo | Agente ignora partes; contexto satura | Mova para `references/`, cite sob demanda |
| Passo sem entrada/saída | Agente pula ou repete etapas | Especifique `entrada → passo → saída` |
| Script sem condição | Agente executa script desnecessariamente | Diga "execute quando: ..." |
| Sem tratamento de erro | Agente trava ou inventa quando MCP falha | Tabela de erros + retry + degrade |
| Proibições ausentes | Agente generaliza ou invente dados | Liste explicitamente o que NÃO fazer |
| Skill sem teste | Funciona na teoria, falha na prática | Execute os 5 cenários obrigatórios |