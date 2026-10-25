# Guia Prático — Empacotar um Plugin

Um **plugin** é o contêiner de distribuição que junta skills + servidor MCP +
manifest. Baseado em developers.openai.com/plugins e na convenção de plugins
do ecossistema Claude.

---

## 1. O Que É um Plugin

```
meu-plugin/
├── plugin.json              (manifest — nome, versão, skills, apps)
├── skills/
│   ├── minha-skill/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── assets/
│   └── outra-skill/
│       └── SKILL.md
├── agents/
│   └── openai.yaml          (declaração de dependências MCP)
└── .app.json                (mapeamento do servidor MCP, se houver)
```

**Três camadas, três papéis**:
- O **manifest** diz o que o plugin é e o que contém.
- As **skills** ensinam o fluxo.
- O **servidor MCP** fornece dados, auth e ações.

---

## 2. Manifest Mínimo

```json
{
  "name": "dice-roller",
  "version": "1.0.0",
  "description": "Rola dados para jogos de mesa",
  "skills": "./skills/",
  "apps": "./.app.json"
}
```

- `skills` — caminho para o diretório com as skills (uma pasta por skill).
- `apps` — caminho para o mapeamento do servidor MCP (omita se não houver).
- `version` — semver; suba a versão ao republicar.

---

## 3. Declaração de Dependência MCP

Em `agents/openai.yaml`:

```yaml
dependencies:
  tools:
    - type: "mcp"
      value: "dice-roller"
      description: "Rola um dado de N lados"
      transport: "streamable_http"
      url: "https://tinymcp.dev/api/moldy-aloof-zettabyte/mcp"
```

Uma dependência **torna a ferramenta disponível**; ela **não substitui** instruções
de fluxo. A skill precisa dizer qual tool usar, em que ordem, e como tratar
resultado ausente ou ambíguo.

---

## 4. Importar Skill a Partir do MCP

O servidor MCP pode carregar as skills consigo. No portal de submissão, ao
selecionar **Scan Tools**, o cliente importa os arquivos do servidor.

**Importante**: os arquivos importados viram um **snapshot** no rascunho —
o cliente **não** os busca do servidor em runtime. Depois de mudar a skill,
faça deploy do servidor e escaneie de novo antes de submeter uma nova versão.

---

## 5. Regras de Empacotamento

1. **Uma skill, um objetivo reconhecível.** Não empacote "faça tudo".
2. **Skills complementam o MCP** — não duplicam a descrição das tools.
3. **Sem arquivos meta** — `README.md`, `CHANGELOG.md` não vão no pacote.
4. **Referências citadas existem** — o validador checa isso.
5. **Versão consistente** — manifest e frontmatter das skills alinhados.
6. **Teste antes de empacotar** — os 5 casos de cada skill.

---

## 6. Fluxo de Publicação

```
1. Criar/validar skills        → skill-validate.py (0 erros)
2. Testar skills               → skill-test.py (todos passam)
3. Testar servidor MCP         → MCP Inspector
4. Escrever manifest           → plugin.json + agents/openai.yaml
5. Testar localmente           → rodar como plugin em dev
6. Submeter                    → portal / registry
7. Verificar pós-publicação    → instalar e exercitar os fluxos
```

---

## 7. Checklist de Plugin

- [ ] `plugin.json` com nome, versão e caminho de skills
- [ ] Cada skill em sua própria pasta, com `SKILL.md` validado
- [ ] Dependências MCP declaradas em `agents/openai.yaml`
- [ ] Servidor MCP testado no Inspector
- [ ] Nenhum arquivo meta no pacote
- [ ] Nenhum segredo no pacote
- [ ] Versão alinhada entre manifest e skills
- [ ] Fluxo ponta a ponta exercitado antes de submeter

---

## Fontes

- OpenAI — Skills: developers.openai.com/plugins/concepts/skills
- OpenAI — Build skills: developers.openai.com/plugins/build/skills
- MCP — Build with Agent Skills: modelcontextprotocol.io/docs/2026-07-28/develop/build-with-agent-skills