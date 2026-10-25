# skill-creator

## Descrição declarada

Cria, avalia e melhora skills para agentes de IA seguindo práticas de referência (MCP, OpenAI, Claude). Use quando o usuário quiser: criar uma skill nova, revisar uma skill existente, converter instruções em skill, integrar skill com servidor MCP, testar validar ou distribuir uma skill, decidir entre skill vs MCP vs ferramenta nativa, gerar estrutura de skill, validar frontmatter e corpo, adicionar scripts/referências/assets, empacotar skill para distribuição, ou revisar se uma skill está completa e funcional. Suporta skills no formato SKILL.md (Anthropic/OpenAI compatível), integração MCP, criação de servidores MCP e empacotamento de plugins. Usa o servidor MCP 'skill-creator' e os scripts de scaffold/validação/teste para garantir qualidade verificável.

## Origem

| Campo | Valor |
|---|---|
| Repositório | https://github.com/anthropics/skills |
| Caminho | `skills/skill-creator/SKILL.md` |
| Licença | Apache-2.0 (código original da Anthropic) + MIT (partes autorais) |
| Confiança | confirmado |

```bash
npx skills add anthropics/skills@skill-creator
```

A versão local foi reescrita (92 → 463 linhas) e ganhou servidor MCP, validadores e testes. O código de terceiros está preservado em mine/skill-creator/ com LICENSE.txt.

## Recursos

`scripts/`, `references/`, `assets/`

## Tamanho

- `SKILL.md`: 21,486 bytes, 450 linhas de corpo
- Arquivos no diretório: 31
- Versão declarada: 3.0.0
