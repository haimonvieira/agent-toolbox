# brave-search

Servidor MCP via stdio. Estado atual: ativo.

## Registrar

```bash
minis-mcp-cli add --name brave-search --command npx --args "-y @modelcontextprotocol/server-brave-search"
```

## Variáveis de ambiente

O servidor espera estas variáveis. Os valores não estão neste repositório:

- `BRAVE_API_KEY` — [criar](minis://settings/environments?create_key=BRAVE_API_KEY)

## Verificar

```bash
minis-mcp-cli ping brave-search
minis-mcp-cli tools brave-search
```
