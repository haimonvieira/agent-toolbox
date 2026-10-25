# Checklist de Qualidade — Skill Pronta

Use antes de considerar uma skill concluída. Cada item deve ser verificável.

---

## 1. Frontmatter

- [ ] `name` presente, kebab-case `[a-z0-9-]`, ≤ 64 chars, igual ao diretório
- [ ] `metadata.version` presente e em semver (`MAJOR.MINOR.PATCH`)
- [ ] Nenhuma chave fora das permitidas (`name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`)
- [ ] `description` com **25+ palavras** e ≤ 1024 chars
- [ ] `description` sem `<` nem `>` (proibido pela spec)
- [ ] `description` cobre **ativação direta** (o pedido óbvio)
- [ ] `description` cobre **ativação indireta** (variações de linguagem)
- [ ] `description` cobre **exclusão** (o que NÃO deve ativar)
- [ ] `description` menciona dependências (MCP, scripts) quando houver
- [ ] `compatibility` declara servidores MCP, ferramentas e runtime (≤ 500 chars)

## 2. Corpo (SKILL.md)

- [ ] Seção `## Quando usar` com **Gatilhos** e **Não usar**
- [ ] Seção `## Fronteira do fluxo` com **Entrada**, **Passos**, **Saída**
- [ ] Sub-seção **Proibições** com itens explícitos ("NÃO ...")
- [ ] Sub-seção **Pontos de parada** (PERGUNTE / RECUSE)
- [ ] Seção `## Recursos auxiliares` referenciando cada arquivo com **condição de uso**
- [ ] Seção `## Critérios de sucesso` mensurável
- [ ] Seção `## Casos de teste` com os 5 tipos
- [ ] Corpo < 500 linhas (excedente movido para `references/`)
- [ ] Passos numerados, cada um com entrada e saída claras
- [ ] Sem instruções conflitantes com o sistema

## 3. Recursos auxiliares

- [ ] `scripts/` — apenas código **determinístico**, com `--help` ou docstring
- [ ] `references/` — material de consulta, não duplicado no corpo
- [ ] `assets/` — templates prontos para copiar/preencher
- [ ] `tests/test-cases.json` — quando a skill tem scripts testáveis
- [ ] Todo recurso citado no corpo **existe no disco**

## 4. Integração MCP (se aplicável)

- [ ] Skill **não** armazena credenciais
- [ ] Servidor MCP declarado (`agents/openai.yaml` ou equivalente)
- [ ] Transport definido (stdio / streamable_http / sse)
- [ ] Tabela de **tratamento de erro** presente
- [ ] Retry com backoff definido (máx 3 tentativas)
- [ ] Ações irreversíveis têm confirmação ou política explícita
- [ ] Verificação pós-escrita (read-after-write) quando há ação
- [ ] Degradação definida para falha do MCP

## 5. Testes

- [ ] **Direto** — o pedido óbvio ativa a skill
- [ ] **Indireto** — reformulações ativam a skill
- [ ] **Incompleto** — dado faltante gera pergunta, não invenção
- [ ] **Negativo** — pedido próximo **não** ativa
- [ ] **Borda** — dados vazios/ambíguos tratados sem invenção
- [ ] Resultados documentados na tabela do SKILL.md

## 6. Higiene

- [ ] Sem `README.md`, `CHANGELOG.md`, `INSTALLATION_GUIDE.md`
- [ ] Sem credenciais, tokens ou PII
- [ ] Sem explicações de conceitos que o modelo já domina
- [ ] Sem duplicar funcionalidade de outra skill
- [ ] Nome do diretório = `name` do frontmatter

---

## Comandos de Verificação

```bash
# Validação estrutural completa (0 erros = aprovado)
python3 /var/minis/skills/skill-creator/scripts/skill-validate.py /var/minis/skills/<nome>

# Validação estrita (avisos viram erros)
python3 /var/minis/skills/skill-creator/scripts/skill-validate.py /var/minis/skills/<nome> --strict

# Testes automatizados (se houver tests/test-cases.json)
python3 /var/minis/skills/skill-creator/scripts/skill-test.py /var/minis/skills/<nome>

# Conformidade estrita com a spec do Claude (frontmatter)
python3 /var/minis/skills/skill-creator/scripts/quick_validate.py /var/minis/skills/<nome>

# Empacotar para distribuição
python3 /var/minis/skills/skill-creator/scripts/package_skill.py /var/minis/skills/<nome> ./dist

# Via servidor MCP
minis-mcp-cli call skill-creator validate_skill name=<nome>
minis-mcp-cli call skill-creator test_skill name=<nome>
```

---

## Pontuação

| Itens marcados | Veredito |
|---|---|
| Todos de 1–3 e 5 | **Pronta** |
| Falta algo em 1–3 | **Incompleta** — não use ainda |
| Falta algo em 4 | **Quebrada** se depender de MCP |
| Falta algo em 5 | **Não testada** — risco alto |
| Falta algo em 6 | **Suja** — limpe antes de publicar |