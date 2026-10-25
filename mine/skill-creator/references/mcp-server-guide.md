# Guia Prático — Construir um Servidor MCP

Referência para quando a tarefa é criar um **servidor MCP** (não uma skill).
Baseado em modelcontextprotocol.io (2026-07-28) e IBM Developer.

> **Regra de escopo**: construir um servidor MCP é uma tarefa diferente de criar
> uma skill. Se o objetivo é ensinar um *fluxo*, faça uma skill. Se é expor uma
> *capacidade externa*, faça um servidor MCP.

---

## 1. Descoberta Antes do Código

Antes de escrever código, responda (o `build-mcp-server` oficial faz exatamente isto):

| Pergunta | Implicação |
|---|---|
| **A que se conecta?** API na nuvem, processo local, filesystem, hardware | Define o transport |
| **Quem vai usar?** Só você, o time, ou qualquer um que instalar | Define distribuição e auth |
| **Tamanho da superfície?** Poucas operações ou wrap de uma API grande | Define quantas tools expor |
| **Precisa de interação?** Texto simples, input estruturado, widgets | Define elicitation vs texto |
| **Auth upstream?** API key, OAuth 2.0, nenhum | Define o fluxo de auth |

Se a mensagem inicial já cobre isso, pule direto para a recomendação.

---

## 2. Modelos de Deployment

| Modelo | Quando usar | Prós | Contras |
|---|---|---|---|
| **Remote (Streamable HTTP)** | Padrão para API na nuvem | Zero instalação, um deploy serve todos, OAuth funciona | Precisa hospedar |
| **MCP App** | Precisa de widgets (pickers, dashboards, charts) | UI rica no chat | Restrito a clientes com suporte |
| **MCP Bundle (MCPB)** | Servidor precisa tocar a máquina do usuário | Instala sem Node/Python | Só para cenários locais |
| **Local stdio** | Prototipagem | Simples, zero infra | Não distribui; migrar para MCPB depois |

**Regra**: se envolve uma API na nuvem → **remote**. Se precisa ler arquivos locais,
dirigir apps desktop ou falar com localhost → **stdio/MCPB**.

---

## 3. Desenho de Ferramentas (Tools)

A parte que mais impacta a qualidade. Reoriente-se do determinístico para o
não-determinístico: o modelo decide quando e com quais argumentos chamar.

### Princípios

1. **Um nome que o modelo entende**, não um nome interno.
   - Ruim: `svcAcct_upd`
   - Bom: `update_account_email`

2. **Descrição como contrato de uso**, não como documentação técnica.
   - Diga *o que faz* e *quando usar*.
   - Diga *o que NÃO faz* (limites).
   - Inclua sinônimos PT/EN quando o cliente for multilíngue.

3. **Schema estrito e tipado** — use `enum` para valores válidos, `required` para
   obrigatórios, `default` para opcionais.

4. **Erros acionáveis** — não devolva "error 400". Devolva o que o modelo deve fazer:
   ```json
   {"isError": true, "message": "Cliente não encontrado. Verifique o ID ou chame list_customers."}
   ```

5. **Idempotência** — ações que podem repetir em retry devem aceitar `idempotency_key`.

6. **Granularidade** — menos tools, mais claras. 100 tools degradam a seleção.
   Prefira uma tool `search` parametrizada a 20 tools `get_X`.

7. **Sem efeitos colaterais ocultos** — se `get_report` também grava no banco, renomeie.

### Exemplo de schema

```json
{
  "name": "create_issue",
  "description": "Cria um ticket. Use quando o usuário reportar bug, erro ou falha. Não use para dúvidas — use create_kb_article.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": {"type": "string", "description": "Resumo em 1 linha"},
      "priority": {"type": "string", "enum": ["baixa", "media", "alta", "urgente"], "default": "media"},
      "idempotency_key": {"type": "string", "description": "Chave para evitar duplicata em retry"}
    },
    "required": ["title"]
  }
}
```

---

## 4. O Que Expor

Um servidor MCP expõe três tipos de capacidade:

| Tipo | O que é | Quando usar |
|---|---|---|
| **Tools** | Funções que o modelo chama | Ações e consultas |
| **Resources** | Dados que o app fornece ao agente | Arquivos, schemas, configuração |
| **Prompts** | Templates que o usuário dispara | `/resumir`, `/revisar` |

A maioria dos servidores começa só com tools. Adicione resources quando houver
dados de contexto estáveis; prompts quando houver fluxos repetíveis pelo usuário.

---

## 5. Autenticação

| Tipo | Quando | Implementação |
|---|---|---|
| **API key** | Serviços internos, simples | Header/query; nunca no corpo; nunca logado |
| **OAuth 2.0/2.1** | Serviços do usuário (Google, GitHub) | Fluxo com redirect; tokens no servidor |
| **Nenhuma** | Dados públicos | — |

**Regras**:
- O servidor guarda o token; o cliente (agente) nunca vê.
- Nunca peça credencial no chat.
- Use PKCE para OAuth público.
- Marque tools destrutivas para exigir confirmação no cliente.

---

## 6. Segurança (mínimo obrigatório)

- **Não confie na entrada** — valide contra o schema antes de executar.
- **Sandbox** para servidores locais: rode com o menor privilégio possível.
- **Sem execução arbitrária** — nada de `eval` sobre argumento do modelo.
- **Path traversal** — normalize e confira limites ao ler/escrever arquivos.
- **Rate limiting** — proteja recursos caros.
- **Logs sem segredos** — nunca logue tokens ou PII.
- **Confirmação** para ações irreversíveis (delete, transfer, publicação).

---

## 7. Entregáveis de Qualidade

- **MCP Inspector** — teste tools, resources e prompts interativamente antes de publicar.
- **Erros tratados** — cada tool devolve `isError` com mensagem acionável.
- **README mínimo** só se for publicar; caso contrário, documente no `SKILL.md` da skill que o usa.
- **Versão** nos metadados do servidor.

---

## 8. Ponte Servidor ↔ Skill

Um servidor MCP raramente é útil sozinho para um agente: ele dá as ferramentas,
mas não o *fluxo*. Combine:

```
Servidor MCP: expõe create_issue, get_issue_status, list_customers
Skill:        ensina quando criar ticket, com qual prioridade, o que verificar antes,
              como tratar falha, e qual o formato da resposta final
```

Declare a dependência na skill e escreva a tabela de tratamento de erro
(veja `references/mcp-integration-patterns.md`).

---

## 9. Checklist de Servidor MCP

- [ ] Discovery respondido (conexão, público, superfície, interação, auth)
- [ ] Deployment escolhido (remote / MCPB / stdio) e justificado
- [ ] Tools com nomes claros e descrições de uso (não técnicas)
- [ ] Schemas tipados com `enum`, `required`, `default`
- [ ] Erros acionáveis com `isError`
- [ ] Idempotência onde há retry
- [ ] Auth implementada; segredos fora do cliente
- [ ] Validação de entrada e proteção contra path traversal
- [ ] Confirmação para ações irreversíveis
- [ ] Testado no MCP Inspector
- [ ] Skill companheira criada para o fluxo (se aplicável)

---

## Fontes

- MCP — Build with Agent Skills: modelcontextprotocol.io/docs/2026-07-28/develop/build-with-agent-skills
- MCP — Build an MCP server: modelcontextprotocol.io/docs/2026-07-28/develop/build-server
- MCP — Security Best Practices: modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices
- MCP — Inspector: modelcontextprotocol.io/docs/2026-07-28/tools/inspector