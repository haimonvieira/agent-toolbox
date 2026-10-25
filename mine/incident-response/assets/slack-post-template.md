# Template — Post de Slack para Incidente

Use este template para formatar o comunicado de incidente. Preencha os campos
entre colchetes. Mantenha o tom factual e direto — sem especulação.

---

```
🚨 *INCIDENTE EM PRODUÇÃO* — [GRAVIDADE: CRÍTICA / ALTA / MÉDIA / BAIXA]

*Serviço afetado:* [nome do serviço]
*Janela:* [início] → [fim ou "em andamento"]
*Impacto:* [descrição objetiva do que os usuários não conseguem fazer]

*Causa provável:*
[1-2 frases baseadas exclusivamente nos log — não especule]

*Ações já tomadas:*
• [ação 1]
• [ação 2]

*Próximos passos:*
• [próximo passo 1]
• [próximo passo 2]

*Nível de confiança:* [X]% — [justificativa curta se < 70%]

*Ticket:* [link do JIRA ou "ticket será criado"]

_Acompanhe este thread para atualizações._
```

---

## Regras de Preenchimento

1. **Impacto** deve ser descritivo e mensurável. Evite "sistema lento".
   Prefere: "checkout indisponível para 40% dos usuários, taxa de erro 5xx = 35%".

2. **Causa provável** só pode mencionar o que os logs efetivamente mostram.
   Se não tiver certeza, escreva: "causa ainda em investigação — logs sugerem [X]".

3. **Ações já tomadas** devem ser reais. Se nenhuma foi tomada, diga:
   "nenhuma ação foi tomada — incidente acaba de ser reportado".

4. **Nível de confiança**:
   - 90-100%: log completo com stack trace e contexto de deploy
   - 70-89%: log parcial mas com erro claro
   - 50-69%: log ambíguo, múltiplos candidatos
   - < 50%: log insuficiente — marque e peça mais dados

5. **Tom**: nunca use linguagem alarmista. Seja direto e técnico.

6. **Não inclua** stack traces completas, dados de usuário, chaves de API ou
   informações de infraestrutura interna (IPs, senhas, URLs de admin).

## Exemplo Preenchido

```
🚨 *INCIDENTE EM PRODUÇÃO* — GRAVIDADE: ALTA

*Serviço afetado:* pagamento-api
*Janela:* 2024-01-15 14:22:30 → em andamento
*Impacto:* 60% das tentativas de checkout falham com HTTP 500.
           Estima-se R$ 15K/hora em vendas perdidas.

*Causa provável:*
Connection pool do banco de dados esgotado (pool exhausted).
Múltiplos erros "Connection pool exhausted" a partir das 14:22.

*Ações já tomadas:*
• Revisado histórico de deploys — nenhum deploy recente
• Aumentado temporary max pool size de 20 para 50

*Próximos passos:*
• Investigar query que não libera conexão (identificada no log)
• Verificar se há vazão anormal de tráfego

*Nível de confiança:* 80% — pool exhaustion confirmado; causa raiz da sobrecarga ainda em investigação.

*Ticket:* INC-1423

_Acompanhe este thread para atualizações._
```