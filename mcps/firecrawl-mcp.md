# firecrawl-mcp

Servidor MCP via stdio. Estado atual: ativo.

## Registrar

```bash
minis-mcp-cli add --name firecrawl-mcp --command npx --args "-y firecrawl-mcp"
```

## Variáveis de ambiente

O servidor espera estas variáveis. Os valores não estão neste repositório:

- `FIRECRAWL_API_KEY` — [criar](minis://settings/environments?create_key=FIRECRAWL_API_KEY)

## Verificar

```bash
minis-mcp-cli ping firecrawl-mcp
minis-mcp-cli tools firecrawl-mcp
```
