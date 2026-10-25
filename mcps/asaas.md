# asaas

Servidor MCP via http. Estado atual: ativo.

## Registrar

```bash
minis-mcp-cli add --name asaas --url "https://docs.asaas.com/mcp" \
  --header "Authorization: <valor>"
```

## Cabeçalhos

Requer: `Authorization`

## Verificar

```bash
minis-mcp-cli ping asaas
minis-mcp-cli tools asaas
```
