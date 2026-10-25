# Metodologia de Teste de Skills

## Por Que Testar

Uma skill que só funciona com o pedido exato do criador é inútil. O teste garante
que a skill ativa corretamente, produz resultados consistentes e não falha em
cenários reais.

**A habilidade de uma skill é medida pela qualidade dos seus testes, não pela
qualidade do seu corpo.**

---

## Os 5 Cenários Obrigatórios

Todo skill deve ser testado com estes cenários. Documente os resultados no
corpo do SKILL.md (seção "Casos de teste").

### 1. Teste Direto (Ativação)

**Objetivo**: A skill ativa quando o usuário pede explicitamente?

**Entrada**: Use a formulação mais óbvia do objetivo da skill.
```
"Gere um relatório de atividade do cliente Acme do último mês"
```

**Critério de aprovação**:
- A skill carrega o corpo completo (não cai em instruções genéricas)
- O fluxo começa pelo passo 1
- Nenhuma pergunta desnecessária é feita

**Se falhar**: A descrição está muito estreita. Adicione sinônimos.

### 2. Teste Indireto (Ativação)

**Objetivo**: A skill ativa quando o usuário usa linguagem diferente?

**Entrada**: Reformulações do mesmo objetivo.
```
"Como foi a atividade da Acme em setembro?"
"Me dê um panorama do que aconteceu com a conta"
"Quais métricas a Acme teve no mês passado?"
"Faça um health check do cliente"
```

**Critério de aprovação**:
- A skill ativa em TODAS as formulações
- O resultado é consistente entre elas

**Se falhar**: A descrição não cobre variações. Expanda com sinônimos e
linguagem casual.

### 3. Teste de Entrada Incompleta (Robustez)

**Objetivo**: A skill pergunta em vez de inventar?

**Entrada**: Dados obrigatórios faltando.
```
"Gere um relatório"
"Analise a atividade"
```

**Critério de aprovação**:
- A skill identifica o dado faltante
- Faz UMA pergunta específica (não genérica)
- Não prossegue com dados inventados

**Se falhar**: A seção "Entrada" ou "Pontos de parada" está incompleta.

### 4. Teste Negativo (Precisão de Ativação)

**Objetivo**: A skill NÃO ativa quando não deveria?

**Entrada**: Pedidos similares mas de domínio diferente.
```
"Agende uma reunião com o cliente Acme"         → skill de agendamento
"Crie um ticket de bug para o erro X"           → skill de suporte
"Me fale sobre a história da empresa Acme"       → conhecimento geral
```

**Critério de aprovação**:
- A skill NÃO é carregada
- O agente usa outro caminho (ou pede esclarecimento)

**Se falhar**: A descrição está muito genérica. Adicione cláusulas
"Não use quando..." para excluir domínios próximos.

### 5. Teste de Borda (Resiliência)

**Objetivo**: A skill lida com dados ausentes, ambíguos ou falha externa?

**Entradas**:
```
"Ciente sem atividade no período"               → dados vazios
"Servidor MCP indisponível"                     → falha externa
"Período futuro"                                → dato inválido
"Nome de cliente que não existe"                → referência inválida
```

**Critério de aprovação**:
- Dados vazios são informados, não mascarados
- Falha externa tem retry + degrade + notificação
- Dado inválido gera pergunta ou recusa clara
- Nenhuma invenção de dados

**Se falhar**: A seção de tratamento de erro ou "Proibições" está ausente.

---

## Critérios de Saída (Além da Ativação)

A ativação correta não é suficiente. Verifique também:

| Critério | Pergunta |
|---|---|
| Consistência | Dois agentes diferentes produzem o mesmo formato? |
| Completude | Todas as seções da saída estão presentes? |
| Fidelidade | A saída contém apenas dados reais (sem invenção)? |
| Ação | O usuário sabe o que fazer depois? |
| Token-efficiency | A saída é direta sem ser rasa? |
| Segurança | Nenhum dado sensível vazou? |

---

## Matriz de Cobertura

Para skills complexas, construa uma matriz:

| Caso | Direto | Indireto | Incompleto | Negativo | Borda | Saída |
|---|---|---|---|---|---|---|
| `skill-A` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `skill-B` | ✅ | ❌ | ✅ | ✅ | ⚠️ | ✅ |

**Regra**: todos os ✅. ⚠️ significa "funciona mas com ressalvas" — documente
a ressalva no corpo da skill.

---

## Automação de Testes

Use `scripts/skill-test.py` para executar testes programáticos em skills que
tenham scripts determinísticos. Para o resto, use a checklist acima manualmente.

### O que automatizar

- Validação de frontmatter (obrigatoriedade, formato)
- Execução de scripts com entradas conhecidas → comparação com saída esperada
- Verificação de que referências citadas existem no disco
- Contagem de tokens do corpo (alerta se > 500 linhas)

### O que NÃO automatizar

- Qualidade da ativação semântica (requer julgamento de modelo)
- Consistência de formato de saída entre execuções humanas
- Julgamento de se a descrição cobre variações de linguagem

---

## Registro de Resultados

Mantenha um registro simples no corpo da skill:

```markdown
## Casos de teste

| # | Tipo | Entrada | Resultado | Refinamento necessário |
|---|---|---|---|---|
| 1 | Direto | "..." | ✅ | — |
| 2 | Indireto | "..." | ❌ | Adicionar sinônimo "balanço" à descrição |
```

Cada falha descoberta em produção deve gerar uma linha nesta tabela e um
refinamento da skill.