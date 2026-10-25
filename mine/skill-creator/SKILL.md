---
name: skill-creator
description: >
  Cria, avalia e melhora skills para agentes de IA seguindo práticas de referência (MCP, OpenAI, Claude).
  Use quando o usuário quiser: criar uma skill nova, revisar uma skill existente, converter instruções em skill,
  integrar skill com servidor MCP, testar validar ou distribuir uma skill, decidir entre skill vs MCP vs ferramenta nativa,
  gerar estrutura de skill, validar frontmatter e corpo, adicionar scripts/referências/assets,
  empacotar skill para distribuição, ou revisar se uma skill está completa e funcional.
  Suporta skills no formato SKILL.md (Anthropic/OpenAI compatível), integração MCP, criação
  de servidores MCP e empacotamento de plugins. Usa o servidor MCP 'skill-creator' e os
  scripts de scaffold/validação/teste para garantir qualidade verificável.
compatibility: python3>=3.8; mcp-server 'skill-creator' (opcional); scripts/skill-scaffold.sh, skill-validate.py, skill-test.py
metadata:
  version: "3.0.0"
---

# Skill Creator — Criação de Skills Fortes

## O Que Esta Skill Faz

Ensina o agente a produzir skills que funcionam de verdade: não só um SKILL.md reciclado,
mas um pacote completo com frontmatter descritivo, corpo instrutivo, recursos auxiliares,
critérios de ativação claros, testes e integração MCP quando necessário.

## Quando usar

### Gatilhos
- O usuário pede para **criar uma skill** nova, gerar estrutura de skill, ou "fazer uma skill para X".
- O usuário pede para **revisar, avaliar ou melhorar** uma skill existente.
- O usuário quer **converter** um processo, prompt ou documento em skill reutilizável.
- O usuário pergunta **skill vs MCP vs ferramenta**, ou quando usar cada um.
- O usuário quer **integrar uma skill com servidor MCP** ou declarar dependência.
- O usuário quer **validar, testar ou empacotar** uma skill para distribuição.
- O usuário quer **adicionar scripts/referências/assets** a uma skill.

### Não usar
- Perguntas conceituais sobre MCP/plugins sem intenção de criar algo — responda diretamente.
- Criação de **servidor MCP** puro (sem skill) — use `mcp-connector` ou `tool-builder`.
- Edição de prompts de sistema (não são skills) — trate como configuração.
- Tarefas que uma skill existente já cobre — invoque a skill diretamente.

## Ferramentas Disponíveis

Esta skill tem três camadas de ferramenta. Use a mais direta para cada caso.

### 1. Servidor MCP `skill-creator` (stdio)

Registrado em `minis-mcp-cli`. Expõe 7 ferramentas:

| Ferramenta | O que faz |
|---|---|
| `create_skill` | Cria estrutura completa (SKILL.md + pastas + tabela de testes) |
| `validate_skill` | Valida frontmatter, seções, referências e casos de teste |
| `test_skill` | Executa `tests/test-cases.json` da skill |
| `list_skills` | Lista skills instaladas com versão e recursos |
| `read_skill` | Lê o SKILL.md de uma skill |
| `get_skill_template` | Devolve o template anotado |
| `update_skill` | Atualiza version/description sem tocar no corpo |

```
minis-mcp-cli call skill-creator create_skill name=minha-skill description="..."
minis-mcp-cli call skill-creator validate_skill name=minha-skill
```

Se o servidor não estiver disponível, use os scripts abaixo — fazem o mesmo.

### 2. Scripts (fallback direto, sempre funcionam)

```bash
cd /var/minis/skills/skill-creator/scripts
./skill-scaffold.sh <nome> "descrição"                 # cria estrutura
python3 skill-validate.py /var/minis/skills/<nome>      # valida (--strict, --json)
python3 skill-test.py   /var/minis/skills/<nome>       # roda testes
python3 quick_validate.py /var/minis/skills/<nome>     # só spec do Claude
python3 package_skill.py  /var/minis/skills/<nome> ./dist  # empacota .skill
sh verify-all.sh                                       # verificação completa (16 checks)
```

### 3. Harness de avaliação por LLM (avançado, opcional)

`scripts/run_eval.py` + `run_loop.py` medem objetivamente se a **descrição**
dispara corretamente, e a reescrevem em loop. Exigem o **Claude Code CLI**
(`claude`), ausente neste ambiente. Detalhes em `references/eval-harness.md`.

### 4. Referências (conhecimento sob demanda)

- `references/mcp-server-guide.md` — construir um **servidor MCP** (deployment, tools, auth, segurança)
- `references/plugin-packaging.md` — empacotar **plugin** (manifest, dependências, publicação)
- `references/mcp-integration-patterns.md` — padrões A/B/C de skill + MCP
- `references/skill-template.md` — template anotado de SKILL.md
- `references/skill-test-checklist.md` — metodologia dos 5 testes
- `references/eval-harness.md` — as duas trilhas de avaliação e limites da spec
- `references/schemas.md` — schemas JSON do harness de avaliação
- `assets/quality-checklist.md` — checklist final de qualidade

## Princípios Fundamentais

### 1. A Skill Ensina "Como", o MCP Dá "Onde", a Ferramenta Define "O Que"

| Camada | Papel | Exemplo |
|---|---|---|
| **Ferramenta (tool use)** | Contracto JSON — o que o agente pode fazer | `create_ticket`, `send_email` |
| **MCP** | De onde vêm as ferramentas — integração padronizada | servidor MCP do Jira, GitHub, Asaas |
| **Skill** | Como usar as ferramentas — fluxo, decisão, formato | "abra um ticket de prioridade alta com este template" |

**Regra de ouro**: competências distintas não se sobrepõem. A skill nunca deve repetir
informação que já está na descrição da ferramenta. O servidor MCP nunca deve decidir
fluxo — ele executa e autentica.

### 2. Divulgação Progressiva (Três Fases)

1. **Descoberta** — o agente lê apenas `name` + `description` (~100 tokens por skill).
   Se a descrição não casar com a intenção do usuário, a skill nunca carrega.
2. **Ativação** — o corpo SKILL.md é carregado (< 5k tokens).
3. **Execução** — referências, scripts e assets são consultados sob demanda (sem limite).

**Consequência prática**: a descrição é a parte mais importante do arquivo.
Se ela falhar, todo o resto é invisível.

### 3. Uma Skill = Um Objetivo Reconhecível do Usuário

Não crie uma skill "faça tudo de marketing". Crie:
- `brand-voice-check` — verifica se um texto segue o guia de voz da marca
- `social-post-generator` — gera post a partir de briefing
- `legal-review-skill` — submete conteúdo para aprovação jurídica

**Critério de divisão**: se duas partes da skill têm gatilhos, entradas ou critérios
de sucesso diferentes, separe em duas skills.

### 4. Scripts para o Determinístico, Skill para o Decisório

- Use **scripts** para: parsing, formatação, cálculos, geração de arquivos, validação de schema.
- Use **instruções** para: escolhas de fluxo, julgamento, tratamento de borda, decisão de parada.

Nunca escreva um script quando a tarefa pode ser feita com ferramentas e instruções existentes.
Nunca deixe para o modelo inferir um passo que um script pode garantir.

---

## Fronteira do fluxo

- **Entrada**: um objetivo de skill (do usuário), um exemplo concreto de uso, e — quando
  existir — a skill em revisão. Sem exemplo concreto, PARE e pergunte.
- **Passos**: siga as 7 fases do processo (Entendimento → Decisão → Frontmatter → Corpo →
  Recursos → Teste → Empacote). Cada fase tem critério de conclusão.
- **Saída**: um diretório de skill completo, validado por `scripts/skill-validate.py`
  (0 erros) e com os 5 casos de teste documentados.
- **Proibições**: veja a seção "Proibições" abaixo.
- **Pontos de parada**: veja a seção "Pontos de parada" abaixo.

## Anatomia de Uma Skill

```
minha-skill/
├── SKILL.md                          (obrigatório — frontmatter + corpo)
├── references/                       (opcional — políticas, schemas, exemplos)
│   ├── policy-compliance.md
│   └── schema-examples.md
├── scripts/                          (opcional — código executável)
│   ├── generate_report.py
│   └── validate_input.sh
├── assets/                           (opcional — templates, arquivos de saída)
│   └── briefing-template.md
└── README.md → NÃO crie. O agente não precisa disso.
```

### SKILL.md — Frontmatter Obrigatório

```yaml
---
name: nome-da-skill
description: >
  Texto longo e exaustivo que diz QUANDO a skill deve ser acionada.
  Inclua variações de linguagem do usuário, objetivos e condições.
  Este é o mecanismo primário de ativação — trate-o como um contrato.
compatibility: ferramentas ou servidores necessários (opcional)
metadata:
  version: "1.0.0"
---
```

**Chaves permitidas pela spec do Claude**: `name`, `description`, `license`,
`allowed-tools`, `metadata`, `compatibility`. Qualquer outra chave é rejeitada
por `quick_validate.py` — por isso a versão vai em `metadata.version`.

**Regras para `description`**:
- Escreva em torno do **objetivo do usuário**, não da implementação.
- Liste condições de ativação exaustivamente — o corpo só é carregado se a descrição casar.
- Use sinonímia: "relatório", "summary", "análise", "balanço" para cobrir variações.
- Mínimo 25 palavras; idealmente 5–8 frases.
- **Não use `<` nem `>`** (proibido pela spec) e fique abaixo de 1024 caracteres.
- Se a skill depende de servidor MCP, mencione aqui.

### SKILL.md — Corpo (Seções Padrão)

```markdown
# Nome da Skill

## Quando usar
Gatilhos explícitos. O que o usuário deve dizer para ativar.
Condições em que a skill NÃO deve ser usada.

## Fronteira do fluxo
- **Entrada**: o que o fluxo espera receber
- **Passos**: sequência numerada (use `scripts/` para passos determinísticos)
- **Saída**: formato e conteúdo do resultado
- **Proibições**: o que o modelo NÃO deve inferir ou substituir
- **Pontos de parada**: quando perguntar ao usuário, quando recusar, quando delegar

## Integração MCP (se aplicável)
- Servidores necessários e ferramentas específicas
- Padrão de autenticação (API key / OAuth 2.1 / sem auth)
- Tratamento de erros e retries
- Declaração de dependência (para OpenAI: `agents/openai.yaml`)

## Recursos auxiliares
- `references/` — consulte quando: [condição]
- `scripts/` — execute quando: [condição]
- `assets/` — use como template para: [condição]

## Critérios de sucesso
O que torna o resultado válido. Mensurável quando possível.

## Casos de teste
Cenários obrigatórios (veja `references/skill-test-checklist.md`).
```

---

## Proibições

- NÃO criar `README.md`, `CHANGELOG.md`, `INSTALLATION_GUIDE.md` ou arquivos meta na skill.
- NÃO escrever uma skill sem antes executar a Fase 1 (entendimento).
- NÃO deixar a descrição com menos de 25 palavras — ela é o gatilho.
- NÃO pular os 5 casos de teste obrigatórios.
- NÃO duplicar funcionalidade de skill ou servidor MCP existente — verifique antes.
- NÃO colocar credenciais, tokens ou chaves de API no SKILL.md.
- NÃO exceder 500 linhas no corpo sem mover conteúdo para `references/`.
- NÃO declarar dependência MCP sem a respectiva tabela de tratamento de erro.

## Pontos de parada

- **PERGUNTE** se o usuário não der um exemplo concreto do caso de uso (Fase 1 exige isso).
- **PERGUNTE** se houver ambiguidade entre "skill pura" e "skill + MCP" e os requisitos não resolverem.
- **PERGUNTE** antes de sobrescrever uma skill existente.
- **RECUSE** criar uma skill que duplique exatamente outra já instalada — sugira melhorar a existente.
- **RECUSE** incluir dados sensíveis (credenciais, PII) no corpo ou nos recursos.
- **RECUSE** criar uma skill "guarda-chuva" com múltiplos objetivos não relacionados — separe.

## Processo de Criação

### Fase 1 — Entendimento (não pule esta etapa)

Antes de escrever qualquer coisa:

1. **Extraia o inventário de casos de uso** do usuário. Peça exemplos concretos.
2. **Identifique o objetivo reconhecível** — qual frase do usuário dispararia isso?
3. **Mapeie fronteiras**:
   - O fluxo precisa de dados externos em tempo real? → MCP
   - Precisa de autenticação complexa? → MCP
   - Precisa de decisão/sequência consistente? → Skill
   - É puramente local/scriptável? → Skill + scripts
4. **Verifique se já existe skill ou MCP** para isso — não reconstrua.

### Fase 2 — Decisão de Arquitetura

Use a matriz abaixo:

| Necessidade | Solução |
|---|---|
| Apenas workflow, sem dados externos | Skill pura |
| Dados externos + auth | MCP + Skill (híbrida) |
| Múltiplos serviços terceirizados | MCP (priorize servidor existente sobre ferramenta custom) |
| Processamento local determinístico | Skill + `scripts/` |
| Output consistente e repetível | Skill + `assets/` |
| Skill que depende de servidor MCP | Declare dependência em `agents/openai.yaml` ou equivalente |

### Fase 3 — Escreva o Frontmatter

Comece pela `description`. Leia-a e pergunte: "se eu fosse o agente, entenderia
que devo ativar esta skill diante de X?" Se não for óbvio, reescreva.

### Fase 4 — Escreva o Corpo

Siga as seções padrão. Mantenha o corpo principal sob 500 linhas — se exceder,
mova conteúdo para `references/`.

**Regras de escrita**:
- Use imperativo: "Parse a entrada", "Chame a ferramenta", "Formate a saída".
- Seja explícito sobre o que o modelo NÃO deve fazer.
- Cada passo deve ter entrada clara e saída definida.
- Referencie recursos auxiliares com caminho e condição de uso.

### Fase 5 — Adicione Recursos

| Pasta | Quando usar | O que colocar |
|---|---|---|
| `references/` | Material de consulta: políticas, schemas, exemplos, background | Arquivos markdown ou JSON |
| `scripts/` | Cálculo determinístico, processamento de arquivos, validação | Python, shell (executable) |
| `assets/` | Templates que o fluxo copia ou transforma | Markdown, JSON, YAML, imagens |

Sempre referencie o recurso no SKILL.md dizendo **quando** carregá-lo ou executá-lo.

### Fase 6 — Teste (obrigatório)

Veja `references/skill-test-checklist.md`. Execute os 5 cenários:

1. **Direto** — pedido explícito que deve ativar
2. **Indireto** — mesmo objetivo com outra formulação
3. **Entrada incompleta** — deve gerar pergunta de follow-up
4. **Negativo** — pedido parecido que NÃO deve ativar
5. **Borda** — dados ambíguos ou ação não suportada

Se o resultado falhar em qualquer cenário, refine:
- Descrição → se a ativação foi errada
- Corpo → se o fluxo foi inconsistente
- Scripts → se o cálculo divergiu

### Fase 7 — Empacote e Versionar

- Versão no frontmatter — em `metadata.version`, formato semver (`MAJOR.MINOR.PATCH`).
- `compatibility` — declare ferramentas, servidores e modelos necessários (≤ 500 chars).
- Empacote com `python3 scripts/package_skill.py <skill> ./dist` → gera `<nome>.skill`.
- Para distribuição em plugin: aponte o manifest para a pasta `skills/`
  (veja `references/plugin-packaging.md`).

---

## Padrões de Integração Skill + MCP

Veja detalhes em `references/mcp-integration-patterns.md`. Resumo:

### Padrão A — Skill que Consome MCP (Leitura)

```
Skill → [decide] → MCP Tool (ler dados) → Skill (analisar, formatar, entregar)
```

Exemplo: `customer-briefing` chama `get_account_activity` (MCP) e produz relatório.

### Padrão B — Skill que Orquestra MCP (Escrita + Validação)

```
Skill → [1] MCP read → [2] decisão → [3] MCP write → [4] verificar → [5] entregar
```

Exemplo: `incident-response` lê logs, decide gravidade, cria ticket, verifica se foi criado.

### Padrão C — Skill com Fallback MCP

Se o servidor MCP falhar, a skill deve ter caminho alternativo:
- Retry com backoff exponencial (máx 3 tentativas)
- Degradar para modo offline se os dados estiverem cache
- Informar ao usuário claramente o que deixou de funcionar

### Regras de Fronteira

- **Skill nunca armazena credenciais** — o servidor MCP lida com auth.
- **Skill nunca ignora erro de MCP** — trate o erro, não o escondo.
- **Skill declara dependência** — para que o runtime possa provisionar o servidor.

---

## Integração MCP

Esta skill **não depende** de servidor MCP — ela é um guia de processo, funciona offline.
Porém, ela **produz** skills que podem depender de MCP, e por isso carrega o conhecimento
de integração necessário:

- O padrão de declaração de dependência (`agents/openai.yaml`, `claude_desktop.config.json`).
- A separação rígida de responsabilidades: skill decide, MCP autentica e executa.
- As tabelas de tratamento de erro obrigatórias para skills com MCP.

Ao criar uma skill que precise de MCP, consulte `references/mcp-integration-patterns.md`
e siga um dos padrões A/B/C conforme o caso.

## O que NÃO Incluir

- `README.md`, `INSTALLATION_GUIDE.md`, `CHANGELOG.md`, `CONTRIBUTING.md` — o agente não precisa.
- Explicações de conceitos que o modelo já sabe (ex: "o que é uma API").
- Longas justificativas de design — mova para `references/` se necessário.
- Scripts que duplicam funcionalidade de ferramentas existentes.
- Instruções conflitantes com as do sistema prompt.

---

## Revisão de Qualidade (Checklist Final)

Antes de considerar uma skill pronta, verifique:

- [ ] `name` presente, kebab-case, ≤ 64 chars
- [ ] `description` cobre ativação direta, indireta e exclusão
- [ ] `description` com 25+ palavras, sem `<`/`>` , ≤ 1024 chars
- [ ] `metadata.version` definida em semver
- [ ] Nenhuma chave de frontmatter fora das permitidas pela spec
- [ ] Seções do corpo seguem o padrão
- [ ] Fronteira do fluxo definida (entrada/saída/proibições/parada)
- [ ] Recursos auxiliares referenciados com condição de uso
- [ ] 5 cenários de teste executados e documentados
- [ ] Skill não duplica outra existente
- [ ] Se usa MCP: dependência declarada, tratamento de erro definido
- [ ] Corpo abaixo de 500 linhas (excedente em `references/`)
- [ ] `skill-validate.py --strict` retorna 0 erros
- [ ] `quick_validate.py` retorna "Skill is valid!"
- [ ] Empacota sem erro com `package_skill.py`

## Compatibilidade com a Spec do Claude

A spec oficial restringe o frontmatter a `name`, `description`, `license`,
`allowed-tools`, `metadata` e `compatibility`. Consequências práticas:

- **Versão vai em `metadata.version`**, nunca como chave de topo.
- Nome é **kebab-case** (`[a-z0-9-]`), sem underscore.
- `description` não pode conter `<` ou `>` e tem limite de 1024 caracteres.
- `compatibility` tem limite de 500 caracteres.

`scripts/quick_validate.py` aplica estas regras. `skill-validate.py` é mais
permissivo (aceita `version:` no topo, convenção Minis) e avisa quando há
divergência — use-o para trabalhar e o `quick_validate.py` antes de distribuir.

---

## Recursos auxiliares

- `references/skill-template.md` — consulte ao escrever o corpo: template anotado com
  cada seção explicada e os erros mais comuns.
- `references/mcp-integration-patterns.md` — consulte quando a skill precisar de MCP:
  padrões A/B/C, auth, declaração de dependência.
- `references/mcp-server-guide.md` — consulte quando a tarefa for **construir um servidor MCP**.
- `references/plugin-packaging.md` — consulte quando a tarefa for **empacotar um plugin**.
- `references/skill-test-checklist.md` — consulte na Fase 6: metodologia dos 5 testes.
- `assets/quality-checklist.md` — consulte antes de declarar a skill pronta.
- `scripts/skill-scaffold.sh` — execute para gerar a estrutura inicial de uma skill.
- `scripts/skill-validate.py` — execute para validar frontmatter, seções e referências.
- `scripts/skill-test.py` — execute para rodar `tests/test-cases.json` da skill.
- `mcp/skill-server.py` — servidor MCP com as 7 ferramentas (registrado como `skill-creator`).

## Critérios de sucesso

- O diretório de skill existe com `SKILL.md` e, se aplicável, `scripts/`, `references/`, `assets/`.
- `python3 scripts/skill-validate.py <skill>` retorna **0 erros**.
- Os 5 casos de teste (direto, indireto, incompleto, negativo, borda) estão documentados
  e foram executados.
- A `description` tem 25+ palavras cobrindo ativação e exclusão.
- Se a skill usa MCP: dependência declarada + tabela de tratamento de erro presente.
- O corpo tem menos de 500 linhas.

## Casos de teste

| # | Tipo | Entrada | Comportamento esperado |
|---|---|---|---|
| 1 | Direto | "Crie uma skill para gerar relatórios semanais" | Ativa, conduz Fase 1 (pede exemplo concreto), depois cria |
| 2 | Indireto | "Como empacoto esse fluxo para reutilizar depois?" | Ativa, propõe estrutura de skill |
| 3 | Incompleto | "Quero uma skill" (sem objetivo) | PERGUNTA qual o objetivo e um exemplo concreto |
| 4 | Negativo | "Me explique o que é MCP" | NÃO ativa (é pergunta conceitual) |
| 5 | Borda | Skill que exige MCP de autenticação complexa | Cria híbrida, declara dependência e tabela de erros |
| 6 | Negativo | "Crie uma skill igual à incident-response" | RECUSA duplicar, sugere melhorar a existente |

## Referências

- Model Context Protocol — [Build with Agent Skills](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-with-agent-skills)
- OpenAI — [Skills – Plugins](https://developers.openai.com/plugins/concepts/skills) e [Build skills](https://developers.openai.com/plugins/build/skills)
- IBM Developer — [Agent Skills e MCP Servers](https://developer.ibm.com/articles/agent-skills-mcp-servers/)
- AgentMelt — [Skills vs MCP vs Tools vs Plugins](https://agentmelt.com/blog/ai-agent-skills-vs-mcp-vs-tools/)