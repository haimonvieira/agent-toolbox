# github

Servidor MCP via stdio. Estado atual: ativo.

## Registrar

```bash
minis-mcp-cli add --name github --command npx --args "-y @modelcontextprotocol/server-github"
```

## Variáveis de ambiente

O servidor espera estas variáveis. Os valores não estão neste repositório:

- `GITHUB_PERSONAL_ACCESS_TOKEN` — [criar](minis://settings/environments?create_key=GITHUB_PERSONAL_ACCESS_TOKEN)

## Verificar

```bash
minis-mcp-cli ping github
minis-mcp-cli tools github
```
