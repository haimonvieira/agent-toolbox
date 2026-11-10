# Prompt — mapear meu stack de IA com evidência de uso

Copie o bloco abaixo e cole no agente que roda no seu computador (omp, Claude Code ou OpenCode).
Ele precisa de acesso ao seu sistema de arquivos — é lá que a evidência está.

---

```
Tarefa: mapear meu stack de IA — o que está configurado e o que eu realmente uso.

REGRAS DE SEGURANÇA (não negociáveis)
- Somente leitura. Não instale, não edite config, não rode instaladores, não faça commit.
- Nunca imprima o valor de uma variável de ambiente, token, chave de API ou header de
  autorização. Relate apenas o NOME da variável (ex: BRAVE_API_KEY: definida).
- Se precisar citar um caminho com usuário, substitua por ~ ou $HOME.
- Não envie nada para a rede.

REGRA DE HONESTIDADE
Cada item que você reportar precisa de uma marca de procedência:
  medido     — você contou ocorrências numa fonte real (log, histórico, config)
  declarado  — está na configuração, mas você não viu uso
  inferido   — você deduziu de contexto, sem fonte direta
Não misture as três. Se não achou evidência, diga "sem evidência" em vez de supor.

FASE 1 — Inventário de configuração

Descubra os arquivos que existem, sem presumir. Para cada agente, teste os caminhos e
registre quais existem de fato:

omp
  ~/.omp/agent/mcp.json, ~/.omp/profiles/*/agent/mcp.json, ./.omp/mcp.json
  ~/.omp/agent/skills/*/SKILL.md, ./.omp/skills/*/SKILL.md
  Também confira se ele importou config de outro cliente (ele faz isso automaticamente).

Claude Code
  ~/.claude.json, ./.mcp.json, ~/.claude/settings.json
  ~/.claude/skills/*/SKILL.md, ./.claude/skills/*/SKILL.md
  ~/.claude/plugins/ (marketplaces e plugins instalados)

OpenCode
  ~/.config/opencode/opencode.json, ./opencode.json
  ~/.config/opencode/skills/*/SKILL.md, ./.opencode/skills/*/SKILL.md
  ./.claude/skills/ e ./.agents/skills/ (o OpenCode também lê esses)

Para cada servidor MCP encontrado, extraia: nome, transporte (stdio/http/sse), comando ou
URL, nomes das variáveis de ambiente exigidas, e enabled sim/não. Não copie valores.

FASE 2 — Evidência de uso

Para cada fonte abaixo, diga se encontrou e quantas amostras leu:

1. Histórico de shell: ~/.zsh_history, ~/.bash_history, ~/.local/share/fish/fish_history
   Conte as 30 ferramentas de linha de comando mais usadas. Interessa especialmente:
   alguma CLI de agente, gerenciadores de pacote, ferramentas de git, e qualquer comando
   que invoque MCP ou skills.

2. Transcrições de sessão do Claude Code: ~/.claude/projects/*/*.jsonl
   Conte chamadas de ferramenta por nome. Isso mostra quais MCPs e skills foram de fato
   invocados.

3. Sessões do omp: procure o diretório de sessões (o doc de "Session format" indica o
   caminho; pode estar em ~/.omp/). Se achar, conte as ferramentas chamadas.

4. Armazenamento do OpenCode: procure em ~/.local/share/opencode/ e ~/.config/opencode/.
   Se houver histórico de sessões, conte as chamadas de ferramenta.

5. Skills: para cada SKILL.md encontrado, verifique se aparece em alguma transcrição ou
   histórico. Uma skill instalada mas nunca citada é "declarada", não "usada".

Se uma fonte não existir, escreva "ausente" e siga. Não invente.

FASE 3 — Cruzamento

Monte três listas separadas:

A. Usado com frequência — evidência medida, ordenado por contagem decrescente.
   Para cada item: nome, contagem, fonte da contagem (arquivo + tipo).

B. Configurado mas sem uso observado — está na config, zero ocorrências nas fontes.

C. Declarado em documentação mas não encontrado no sistema — o que a config referencia
   e não existe mais.

FASE 4 — Saída

Entregue duas coisas.

1) Um resumo em markdown, com no máximo 40 linhas, contendo: as 10 ferramentas mais usadas
   com contagem; os MCPs usados vs apenas configurados; as skills usadas vs apenas
   instaladas; e uma lista curta do que parece morto ou duplicado.

2) Um JSON no schema abaixo, pronto para eu colar em data/ do meu repositório:

{
  "gerado_em": "<ISO 8601>",
  "host": { "os": "...", "agentes_detectados": ["omp", "claude-code", "opencode"] },
  "fontes": [
    { "tipo": "shell_history|transcript|config|skill_dir", "caminho": "~/.zsh_history",
      "existe": true, "amostras": 1234 }
  ],
  "mcps": [
    { "nome": "...", "transporte": "stdio|http", "origem": "~/.claude.json",
      "enabled": true, "env_vars": ["NOME_DA_VAR"], "procedencia": "medido|declarado",
      "usos": 42 }
  ],
  "skills": [
    { "nome": "...", "origem": "~/.claude/skills/x/SKILL.md",
      "procedencia": "medido|declarado", "usos": 7 }
  ],
  "clis": [
    { "comando": "git", "usos": 830, "fonte": "~/.zsh_history", "procedencia": "medido" }
  ],
  "sem_evidencia": ["itens configurados que não apareceram em nenhuma fonte"]
}

Ao final, diga explicitamente quais fontes você NÃO conseguiu ler e por quê. Um mapeamento
com lacuna declarada vale mais que um completo inventado.
```

---

## Por que o prompt é assim

**Ele separa três estados, não dois.** "Instalado" e "usado" não bastam: existe o configurado-que-nunca-roda e o documentado-que-não-existe-mais. Sem essa distinção o inventário vira uma lista de desejos.

**Ele exige a fonte da contagem.** "Usado 42 vezes" sem dizer de onde veio a contagem é opinião. Com a fonte, você pode conferir.

**Ele obriga a declarar o que não conseguiu ler.** Transcrições de sessão têm formatos diferentes em cada agente e podem não existir no seu. Um agente que inventa um mapeamento completo é pior que um que reporta "não achei histórico do omp".

## O que eu não sei, e por isso não afirmei

Os caminhos de **sessão** do omp e do OpenCode eu não verifiquei — a documentação que li cobre configuração de MCP e skills, não onde ficam os logs. O prompt manda o agente procurar e reportar, em vez de assumir um caminho que pode não existir.

Os caminhos de **configuração** (Fase 1) foram verificados na documentação oficial dos três.
