# Agent Toolbox

Setup do meu agente de IA: **36 skills** e **10 servidores MCP** em uso,
cada um com origem, licença e comando de instalação. Atualizado em 25/10/2026.

O repositório tem duas partes:

- **[Recomendações](#recomendações)** — 11 skills que eu uso e indico para quem está começando.
- **[Inventário](#inventário)** — as 36 skills e os 10 MCPs que eu tenho instalados.

As skills recomendadas são referenciadas por **commit**, não copiadas. Dois motivos: os
repositórios de origem recebem push semanal, então uma cópia ficaria defasada; e uma das
skills não declara licença, o que impede redistribuição. Cada ficha traz o commit exato.

Para aplicar no seu agente: `python3 scripts/emit_config.py --tool omp` (ou `claude-code`, `opencode`).
Para consumir por agente: [`catalog.json`](catalog.json).

---

## Como configurar

Cada agente lê MCP e skills de um lugar diferente. Estas são as localizações e os
formatos, verificados na documentação oficial de cada um.

| | omp | Claude Code | OpenCode |
|---|---|---|---|
| MCP (projeto) | `.omp/mcp.json` | `.mcp.json` | `opencode.json` |
| MCP (usuário) | `~/.omp/agent/mcp.json` | `~/.claude.json` | `~/.config/opencode/opencode.json` |
| Bloco raiz | `mcpServers` | `mcpServers` | `mcp` |
| stdio | `command` + `args` | `command` + `args` | `type: local` + `command` (array) |
| remoto | `type: http` + `url` | `type: http` + `url` | `type: remote` + `url` |
| Skills (usuário) | `~/.omp/agent/skills/<nome>/` | `~/.claude/skills/<nome>/` | `~/.config/opencode/skills/<nome>/` |
| Skills (projeto) | `.omp/skills/<nome>/` | `.claude/skills/<nome>/` | `.opencode/skills/<nome>/` |

### omp

Documentação: https://omp.sh/docs/mcp

Arquivos de configuração de MCP:

- projeto: `.omp/mcp.json`
- usuário: `~/.omp/agent/mcp.json`
- perfil: `~/.omp/profiles/<nome>/agent/mcp.json`
- portável: `mcp.json ou .mcp.json na raiz do projeto`

Comandos:

```bash
/mcp add
/mcp list
/mcp reload
/mcp test <nome>
```

Servidor stdio:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/caminho/absoluto"
      ]
    }
  }
}
```

Servidor remoto:

```json
{
  "mcpServers": {
    "exemplo": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <token>"
      }
    }
  }
}
```

Skills:

- usuário: `~/.omp/agent/skills/<nome>/SKILL.md`
- projeto: `.omp/skills/<nome>/SKILL.md`

Observações:

- stdio é o transporte padrão quando type é omitido.
- Um servidor não pode ter command e url ao mesmo tempo.
- Para SSE legado, use type: "sse" explicitamente — URL terminando em /sse não seleciona o transporte sozinha.
- omp importa automaticamente definições de MCP do Claude Code, Codex, Gemini CLI, OpenCode, Cursor, Windsurf e VS Code.
- Descoberta é um nível de profundidade: skills/postgres/SKILL.md é achado, skills/databases/postgres/SKILL.md não.
- Mantenha os arquivos referenciados pelo SKILL.md dentro da mesma pasta da skill.
- /extensions abre a lista de skills; /reload-plugins recarrega a sessão.
- Invocação explícita: /skill:<nome>.

### Claude Code

Documentação: https://docs.claude.com/en/docs/claude-code/mcp

Arquivos de configuração de MCP:

- projeto: `.mcp.json`
- local e usuário: `~/.claude.json`

Comandos:

```bash
claude mcp add <nome> --env CHAVE=valor -- <comando> [args]
claude mcp add --transport http <nome> <url> --header "Authorization: Bearer <token>"
claude mcp list
claude mcp get <nome>
```

Servidor stdio:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/caminho/absoluto"
      ]
    }
  }
}
```

Servidor remoto:

```json
{
  "mcpServers": {
    "exemplo": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "Authorization": "Bearer <token>"
      }
    }
  }
}
```

Skills:

- pessoal: `~/.claude/skills/<nome>/`
- projeto: `.claude/skills/<nome>/`

Observações:

- Sem --transport, o padrão é stdio.
- O -- duplo separa as opções do Claude Code do comando do servidor. Sem ele, flags como -y são lidas como opções do Claude.
- Um bloco com url e sem type é lido como stdio e o servidor é ignorado: inclua "type": "http".
- Escopos: padrão local; use --scope project ou --scope user para mudar.
- O tipo aceita http e streamable-http como sinônimos.
- /skills lista as skills carregadas; /reload-skills recarrega após adicionar uma.
- Skills de plugin chegam por marketplace e são removidas com /plugin uninstall.
- Para impedir que o modelo invoque sozinho, use disable-model-invocation: true no frontmatter.

### OpenCode

Documentação: https://opencode.ai/docs/mcp-servers/

Arquivos de configuração de MCP:

- projeto: `opencode.json ou opencode.jsonc`
- global: `~/.config/opencode/opencode.json`

Servidor stdio:

```json
{
  "mcp": {
    "filesystem": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/caminho/absoluto"
      ],
      "enabled": true
    }
  }
}
```

Servidor remoto:

```json
{
  "mcp": {
    "exemplo": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer <token>"
      }
    }
  }
}
```

Skills:

- projeto: `.opencode/skills/<nome>/SKILL.md`
- global: `~/.config/opencode/skills/<nome>/SKILL.md`
- compatível com Claude: `.claude/skills/ e ~/.claude/skills/`
- compatível com agentes: `.agents/skills/ e ~/.agents/skills/`

Observações:

- O bloco se chama mcp, não mcpServers.
- type é obrigatório: local ou remote.
- command é um array, não uma string.
- Variáveis vão em environment, dentro do bloco do servidor.
- enabled: false desliga o servidor sem removê-lo da configuração.
- Skills são carregadas sob demanda pela skill tool nativa.
- Em caminhos de projeto, o OpenCode sobe do diretório atual até a raiz do worktree do git.

---

## Como descobrir skills

O ecossistema tem mais de 1,5 milhão de skills. Estes são os caminhos que eu uso para encontrar uma skill quando não sei que ela existe.

### find-skills

Uma skill que pesquisa catálogos por palavra-chave e devolve candidatos com install count e origem. É o ponto de entrada: quando peço 'acha uma skill para X', é ela que roda.

- Como usar: npx skills add vercel-labs/skills@find-skills
- Onde: https://github.com/vercel-labs/skills
- Escopo: agrega os catálogos abaixo · Autenticação: nenhuma
- Ressalva: A versão local foi estendida para consultar o omgskills via MCP como fonte primária. A versão do repositório de origem não faz isso.

### omgskills

Catálogo público com cerca de 55 mil skills. Exposto como servidor MCP read-only, sem autenticação. Traz plano de instalação pinada (repo + path + commit) quando consegue resolver.

- Como usar: `Servidor MCP remoto. Registre em .omp/mcp.json, .mcp.json ou opencode.json com type http e url https://omgskills.com/mcp — veja a ficha em mcps/omgskills.md`
- Onde: https://omgskills.com/mcp
- Escopo: ≈55.000 skills · Autenticação: nenhuma
- Ressalva: Os metadados nem sempre estão atualizados: o star count do devops-engineer vinha como 8.810 quando o repositório tinha 12.043. Resolva o pin na fonte antes de confiar.

### skills.sh (npx skills)

O maior diretório: cerca de 1,5 milhão de skills. Feito pela Vercel, código aberto em vercel-labs/skills. Tem leaderboard (all time, trending 24h, hot), packs, topics, uma seção Official e auditoria de segurança combinando Gen Agent Trust Hub, Socket e Snyk.

- Como usar: `npx skills find <consulta>  ·  npx skills add <owner/repo>  ·  npx skills use <owner/repo@skill>  ·  npx skills list  ·  npx skills update`
- Onde: https://skills.sh/
- Escopo: ≈1.500.000 skills · Autenticação: nenhuma
- Ressalva: Não expõe API nem llms.txt para agentes: /llms.txt, /agents.md e /api/skills respondem 404. O acesso por agente é pelo CLI. O add instala o estado atual do branch, mas grava skills-lock.json, e `npx skills experimental_install` restaura as versões registradas nele.

### AAS — Agentic Awesome Skills

Catálogo de 2.750 skills com servidor MCP local (stdio) e CLI. O diferencial é o compose_stack: em vez de buscar uma skill por vez, você declara as capacidades do projeto e ele monta um stack, cobrindo cada capacidade ou reportando lacuna. Expõe search_skills, get_skill, compose_stack, inspect_stack e diff_stack.

- Como usar: `git clone https://github.com/sickn33/agentic-awesome-skills   # MIT no código, CC BY 4.0 no conteúdo`
- Onde: https://aaskills.tech/
- Escopo: ≈2.750 skills · Autenticação: nenhuma
- Ressalva: O Core não rankeia nem recomenda: registra e valida a escolha do agente. Útil quando o problema é cobertura de capacidades, não descoberta.

---

## Recomendações

Estas 11 skills foram verificadas uma a uma: o commit existe, o arquivo está no caminho
indicado e a licença foi conferida. Cada uma tem uma ficha com o commit exato.

### Escrever e encontrar skills

#### [find-skills](recommended/find-skills.md) · essencial

Pesquisa catálogos por palavra-chave e devolve candidatos com install count e origem. É o que roda quando peço 'acha uma skill para X'. A versão local foi estendida para consultar o omgskills via MCP como fonte primária.

- Repositório: [vercel-labs/skills](https://github.com/vercel-labs/skills) — 36,458 stars, último push 2026-10-19
- Caminho: `skills/find-skills/SKILL.md`
- Commit: `a80e4c9d12d6`
- Licença: MIT
- Instalar: `npx skills add vercel-labs/skills@find-skills`

#### [writing-for-agents](recommended/mattpocock-writing-for-agents.md) · recomendada

Cobre o que o agente lê fora das skills: AGENTS.md, CLAUDE.md e documentação de projeto. Esses arquivos costumam ser escritos uma vez e nunca revisados.

- Repositório: [mattpocock/skills](https://github.com/mattpocock/skills) — 302,805 stars, último push 2026-10-22
- Caminho: `skills/productivity/writing-for-agents/SKILL.md`
- Commit: `5beb35b040e3`
- Licença: MIT
- Instalar: `npx skills add mattpocock/skills@writing-for-agents`

#### [writing-skills](recommended/obra-superpowers-writing-skills.md) · essencial

Instruções para escrever uma skill: frontmatter, seções, casos de teste e iteração. É o mesmo problema que o harness de avaliação da Anthropic resolve por ferramenta, aqui como texto que o agente lê.

- Repositório: [obra/superpowers](https://github.com/obra/superpowers) — 304,782 stars, último push 2026-10-23
- Caminho: `skills/writing-skills/SKILL.md`
- Commit: `2ce8aa15d05b`
- Licença: MIT
- Instalar: `npx skills add obra/superpowers@writing-skills`

### Engenharia

#### [ponytail](recommended/dietrichgebert-ponytail.md) · essencial

Restringe a mudança ao mínimo que resolve a tarefa e pede respostas de uma leitura. Três níveis: lite, full (padrão) e ultra. O repositório traz ainda variantes para auditoria, dívida técnica e revisão.

- Repositório: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) — 175,787 stars, último push 2026-10-18
- Caminho: `skills/ponytail/SKILL.md`
- Commit: `09c434ab73ca`
- Licença: MIT
- Instalar: `npx skills add DietrichGebert/ponytail@ponytail`

#### [pr](recommended/mattpocock-pr.md) · recomendada

Escreve o corpo de um pull request com o contexto que a revisão precisa: o que mudou, por quê, e como foi verificado.

- Repositório: [mattpocock/skills](https://github.com/mattpocock/skills) — 302,805 stars, último push 2026-10-22
- Caminho: `skills/engineering/pr/SKILL.md`
- Commit: `5beb35b040e3`
- Licença: MIT
- Instalar: `npx skills add mattpocock/skills@pr`

#### [systematic-debugging](recommended/obra-superpowers-systematic-debugging.md) · essencial

Impede propor correção antes de identificar a causa. Define a ordem: reproduzir, isolar, só então corrigir.

- Repositório: [obra/superpowers](https://github.com/obra/superpowers) — 304,782 stars, último push 2026-10-23
- Caminho: `skills/systematic-debugging/SKILL.md`
- Commit: `2ce8aa15d05b`
- Licença: MIT
- Instalar: `npx skills add obra/superpowers@systematic-debugging`

#### [test-driven-development](recommended/obra-superpowers-test-driven-development.md) · recomendada

Exige o teste antes do código de produção, com o teste falhando primeiro. Faz o agente produzir código verificável em vez de código plausível.

- Repositório: [obra/superpowers](https://github.com/obra/superpowers) — 304,782 stars, último push 2026-10-23
- Caminho: `skills/test-driven-development/SKILL.md`
- Commit: `2ce8aa15d05b`
- Licença: MIT
- Instalar: `npx skills add obra/superpowers@test-driven-development`

### Planejamento e verificação

#### [verification-before-completion](recommended/obra-superpowers-verification-before-completion.md) · essencial

Exige rodar o comando de verificação e mostrar a saída antes de afirmar que algo funciona. Evita o agente declarar concluído o que não testou.

- Repositório: [obra/superpowers](https://github.com/obra/superpowers) — 304,782 stars, último push 2026-10-23
- Caminho: `skills/verification-before-completion/SKILL.md`
- Commit: `2ce8aa15d05b`
- Licença: MIT
- Instalar: `npx skills add obra/superpowers@verification-before-completion`

#### [writing-plans](recommended/obra-superpowers-writing-plans.md) · essencial

Produz o plano antes de tocar no código. Corrigir um plano custa minutos; corrigir uma implementação custa horas.

- Repositório: [obra/superpowers](https://github.com/obra/superpowers) — 304,782 stars, último push 2026-10-23
- Caminho: `skills/writing-plans/SKILL.md`
- Commit: `2ce8aa15d05b`
- Licença: MIT
- Instalar: `npx skills add obra/superpowers@writing-plans`

### Código desconhecido

#### [acquire-codebase-knowledge](recommended/github-awesome-copilot-acquire-codebase-knowledge.md) · essencial

Mapeia um código desconhecido: pontos de entrada, arquitetura, convenções e um CLAUDE.md inicial. Mantido pelo GitHub no repositório awesome-copilot.

- Repositório: [github/awesome-copilot](https://github.com/github/awesome-copilot) — 40,385 stars, último push 2026-10-23
- Caminho: `skills/acquire-codebase-knowledge/SKILL.md`
- Commit: `d85f762d6e52`
- Licença: MIT
- Instalar: `npx skills add github/awesome-copilot@acquire-codebase-knowledge`

### DevOps

#### [devops-engineer](recommended/jeffallan-devops-engineer.md) · recomendada

Operações de infraestrutura e CI/CD sem exigir uma stack específica. Licença MIT e repositório ativo. Obs.: o catálogo do omgskills mostra 8.810 stars; o repositório tem 12.043 — o catálogo está desatualizado.

- Repositório: [jeffallan/claude-skills](https://github.com/jeffallan/claude-skills) — 12,050 stars, último push 2026-10-24
- Caminho: `skills/devops-engineer/SKILL.md`
- Commit: `9e7dbd688015`
- Licença: MIT
- Instalar: `npx skills add jeffallan/claude-skills@devops-engineer`

#### [devops](recommended/mrgoonie-claudekit-devops.md) · referencia-only

Cobre Cloudflare, Docker, GCP, Kubernetes e GitOps. Consta aqui apenas como referência: o repositório não declara licença, então não há permissão de redistribuição nem de instalação automatizada. O último push foi em abril de 2026.

- Repositório: [mrgoonie/claudekit-skills](https://github.com/mrgoonie/claudekit-skills) — 2,228 stars, último push 2026-04-03
- Caminho: `.claude/skills/devops/SKILL.md`
- Commit: `80113d86bc44`
- Licença: não declarada
- Atenção: Sem licença declarada — consulte a fonte diretamente, não redistribua.

---

## Inventário

Skills instaladas no meu ambiente. 7 têm origem confirmada, 29 não. As
sem origem aparecem marcadas como não documentadas, e não com uma origem suposta.

5 skills do ambiente original não são publicadas aqui por dependerem de
CLIs e caminhos daquele sistema (config de app, serviços de fundo, pacotes Alpine).
Continuam em `data/skills.json`; ficam fora do README, das fichas e do catalog.json.

| Categoria | Skills |
|---|---|
| Criar e orquestrar skills | 9 |
| Memória | 7 |
| Engenharia de código | 9 |
| GitHub | 3 |
| Web e busca | 6 |
| APIs e dados | 2 |

### Criar e orquestrar skills

| Skill | O que faz | Origem |
|---|---|---|
| [`find-skills`](skills/find-skills.md) | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a … | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| [`mcp-connector`](skills/mcp-connector.md) | Connect to and interact with Model Context Protocol (MCP) servers: discover tools, initialize sessio… | não documentada |
| [`production-agent-public`](skills/production-agent-public.md) | 生产级 ReAct Agent 技能。当用户说"生产级方案"、"可部署代码"、"Production Agent"、 "ReAct格式"、"帮我写一个能跑的"、"长期稳定运行"、"生产环境"、"直接部… | não documentada |
| [`saa-orchestrator`](skills/saa-orchestrator.md) | Sistema Agente Autônomo que orquestra o ciclo Executor→Crítico→Otimizador e delega para Multi-Agente… | não documentada |
| [`self-improving-agent`](skills/self-improving-agent.md) | Self-improvement logging and closed-loop feedback: Trigger when a command or operation fails, the us… | não documentada |
| [`self-learning`](skills/self-learning.md) | Capture a hard-won "golden path" from the current session as a reusable Agent Skill, so future sessi… | não documentada |
| [`skill-creator`](skills/skill-creator.md) | Cria, avalia e melhora skills para agentes de IA seguindo práticas de referência (MCP, OpenAI, Claud… | [anthropics/skills](https://github.com/anthropics/skills) |
| [`skill-orchestrator`](skills/skill-orchestrator.md) | Planejar seleção de capacidades e orientar execução pelo coordenador. Usar em tarefas multi-etapa e … | não documentada |
| [`tool-builder`](skills/tool-builder.md) | Create structured tools and APIs for autonomous agents to execute actions and retrieve external data… | não documentada |

### Memória

| Skill | O que faz | Origem |
|---|---|---|
| [`memory-defrag`](skills/memory-defrag.md) | Defragment and reorganize agent memory files: split bloated files, merge duplicates, remove stale in… | não documentada |
| [`memory-ingest`](skills/memory-ingest.md) | Process unstructured external input (meeting transcripts, conversation logs, pasted documents) into … | não documentada |
| [`memory-notes`](skills/memory-notes.md) | How to write well-structured Basic Memory notes: frontmatter, observations with semantic categories,… | não documentada |
| [`memory-reflect`](skills/memory-reflect.md) | Sleep-time memory reflection: review recent conversations and daily notes, extract insights, and con… | não documentada |
| [`memory-schema`](skills/memory-schema.md) | Schema lifecycle management for Basic Memory: discover unschemaed notes, infer schemas, create and e… | não documentada |
| [`memory-supermemory`](skills/memory-supermemory.md) | Backend adapter for Basic Memory skills (memory-notes, memory-tasks, memory-schema, memory-ingest, m… | não documentada |
| [`memory-tasks`](skills/memory-tasks.md) | Task management via Basic Memory schemas: create, track, and resume structured tasks that survive co… | não documentada |

### Engenharia de código

| Skill | O que faz | Origem |
|---|---|---|
| [`context-map`](skills/context-map.md) | Generate a map of all files relevant to a task before making changes | não documentada |
| [`executing-plans`](skills/executing-plans.md) | Use when you have a written implementation plan to execute in a separate session with review checkpo… | [obra/superpowers](https://github.com/obra/superpowers) |
| [`hermes-codebase-inspection`](skills/hermes-codebase-inspection.md) | Inspect codebases w/ pygount: LOC, languages, ratios. | não documentada |
| [`incident-response`](skills/incident-response.md) | Diagnostica incidentes de producao a partir de logs e gera plano de acao com post de Slack, checklis… | local |
| [`openrouter-rate-limits`](skills/openrouter-rate-limits.md) | Understand and handle OpenRouter rate limits. Use when hitting 429 errors, | não documentada |
| [`refactor-plan`](skills/refactor-plan.md) | Plan a multi-file refactor with proper sequencing and rollback steps | não documentada |
| [`systematic-debugging`](skills/systematic-debugging.md) | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes | [obra/superpowers](https://github.com/obra/superpowers) |
| [`verification-before-completion`](skills/verification-before-completion.md) | Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - req… | [obra/superpowers](https://github.com/obra/superpowers) |
| [`writing-plans`](skills/writing-plans.md) | Use when you have a spec or requirements for a multi-step task, before touching code | [obra/superpowers](https://github.com/obra/superpowers) |

### GitHub

| Skill | O que faz | Origem |
|---|---|---|
| [`gh-cli`](skills/gh-cli.md) | GitHub CLI (gh) operational quick reference for repos, issues, pull requests, Actions, releases, aut… | não documentada |
| [`github-search`](skills/github-search.md) | Search GitHub repositories, issues, users, and code via the REST API. Use when the user asks to find… | não documentada |
| [`hermes-github-auth`](skills/hermes-github-auth.md) | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login. | não documentada |

### Web e busca

| Skill | O que faz | Origem |
|---|---|---|
| [`browser-automation`](skills/browser-automation.md) | Browser automation powers web testing, scraping, and AI agent | não documentada |
| [`exa-search`](skills/exa-search.md) | Search the web, read webpages as markdown, and run filtered web retrieval with Exa MCP. Use this ski… | não documentada |
| [`firecrawl`](skills/firecrawl.md) | Firecrawl gives AI agents and apps fast, reliable web context with strong search, scraping, and inte… | não documentada |
| [`free-tts`](skills/free-tts.md) | 免费语音合成（edge-tts），无需 API Key 无需注册。将文本转为 mp3 音频文件。 当用户说"朗读""语音合成""文字转语音""TTS""生成音频""读一下" "读出来""念一下""听一… | não documentada |
| [`web-content-extractor`](skills/web-content-extractor.md) | Clean and extract the main body content from a webpage URL. Use this skill whenever the user asks to… | não documentada |
| [`web-search`](skills/web-search.md) | General web search skill that uses browser automation with multiple search engines and selects the p… | não documentada |

### APIs e dados

| Skill | O que faz | Origem |
|---|---|---|
| [`asaas-mcp`](skills/asaas-mcp.md) | Interact with Asaas services via the public MCP server. Configure your MCP client to connect to http… | não documentada |
| [`hermes-maps`](skills/hermes-maps.md) | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM. | não documentada |

---

## Servidores MCP

| Servidor | Transporte | Precisa de | Estado |
|---|---|---|---|
| [`asaas`](mcps/asaas.md) | http | header `Authorization` | ativo |
| [`brave-search`](mcps/brave-search.md) | stdio | `BRAVE_API_KEY` | ativo |
| [`everything`](mcps/everything.md) | stdio | — | ativo |
| [`fetch`](mcps/fetch.md) | stdio | — | desligado |
| [`filesystem`](mcps/filesystem.md) | stdio | — | ativo |
| [`firecrawl-mcp`](mcps/firecrawl-mcp.md) | stdio | `FIRECRAWL_API_KEY` | ativo |
| [`github`](mcps/github.md) | stdio | `GITHUB_PERSONAL_ACCESS_TOKEN` | ativo |
| [`omgskills`](mcps/omgskills.md) | http | — | ativo |
| [`sequential-thinking`](mcps/sequential-thinking.md) | stdio | — | ativo |
| [`skill-creator`](mcps/skill-creator.md) | stdio | — | ativo |

As credenciais não estão neste repositório. Cada ficha diz qual variável de ambiente ou
cabeçalho o servidor espera.

---

## Mapear um stack

Este repositório nasceu de um mapeamento do meu ambiente. Para fazer o seu, há um
prompt pronto em [`prompts/map-ai-stack.md`](prompts/map-ai-stack.md):

Ele separa o que está **instalado** do que é **realmente usado**, exigindo a fonte de
cada contagem, e termina com um JSON no formato de `data/`. Roda em omp, Claude Code
ou OpenCode — precisa de acesso ao sistema de arquivos, porque a evidência está lá.

---

## Aplicar a configuração

O catálogo é a fonte. Este script traduz para o formato do seu agente:

```bash
python3 scripts/emit_config.py --tool omp            # imprime o JSON
python3 scripts/emit_config.py --tool opencode       # imprime o JSON
python3 scripts/emit_config.py --tool claude-code    # imprime os comandos

python3 scripts/emit_config.py --tool omp --write    # grava em .omp/mcp.json
python3 scripts/emit_config.py --tool opencode --write   # grava em opencode.json
python3 scripts/emit_config.py --tool opencode --only omgskills
```

Com `--write`, chaves já existentes no arquivo são preservadas; só o bloco de MCP é
mesclado. Substitua `COLE_O_VALOR_AQUI` pelos valores reais depois.

Manter o inventário em dia:

```bash
python3 scripts/gather.py        # relê o ambiente para data/*.json
python3 scripts/resolve_pins.py  # re-resolve os commits das recomendações
python3 scripts/build.py         # regenera README, catalog.json e as fichas
python3 scripts/verify_pins.py   # confere se os commits ainda existem
```

---

## Licença

MIT ([LICENSE](LICENSE)) para a documentação e os scripts deste repositório. As skills e
servidores MCP referenciados são de terceiros e mantêm suas licenças, indicadas em cada
ficha. Nada de terceiros é redistribuído. Ver [NOTICE](NOTICE) para as atribuições.

---

## Environment audit (Phase 1–3)

This repository also contains a sanitized, reproducible audit of the machine where the agent setup
runs. It is additive to the curated catalog above and does not replace it.

- [Audit overview](audit/README.md)
- [Audit findings](audit/AUDIT-REPORT.md)
- [Remediation gates and status](audit/approval-gates.md)
- [Pre-publication checks](audit/pre-publish-check.md)
- [Machine-readable inventories](inventory/)
- [Architecture and ownership graph](docs/architecture.md)
- [Harness notes](docs/harnesses.md) · [Skills](docs/skills.md) · [MCPs](docs/mcps.md) · [Plugins](docs/plugins.md) · [Hooks](docs/hooks.md)

No secrets, private project names, or local absolute paths are included.

## Self-audit

The repository can compare its documented inventory with the real local agent environment and
produce deterministic drift reports.

```bash
./scripts/audit.sh                  # full read-only local audit
./scripts/audit.sh --quick          # fast metadata/config check
./scripts/verify.sh                 # repository-only validation (fast)
./scripts/check-links.sh            # public external links
```

- Local audit reports: `audit/drift-report.md`, `audit/drift-report.yaml`, `audit/backlog.md`,
  `audit/update-suggestions.md`.
- Baseline: `local-state/baseline.yaml` (committed); current state is gitignored.
- Policy: `config/drift-policy.yaml`.
- CI validates repository data only; it cannot inspect the local machine.
- Schemas: `schemas/inventory.schema.json`, `schemas/snapshot.schema.json`.
- Policy: `config/drift-policy.yaml`; backlog seeds: `config/backlog.yaml`.
- Tests: `tests/test_audit.py`; CI: `.github/workflows/validate-toolbox.yml`.
- Full details: [docs/self-audit.md](docs/self-audit.md).

> The audit is read-only by default and never installs, removes, updates, or executes unknown agent
> tooling.
