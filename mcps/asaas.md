# asaas

Servidor MCP via http. Estado no ambiente de origem: ativo.

## Configurar

A mesma configuração nos três formatos. Troque `COLE_O_VALOR_AQUI` pelo valor real e mantenha a credencial fora do repositório.

### omp

Em `.omp/mcp.json`:

```json
{
  "mcpServers": {
    "asaas": {
      "type": "http",
      "url": "https://docs.asaas.com/mcp",
      "headers": {
        "Authorization": "Bearer COLE_O_VALOR_AQUI"
      }
    }
  }
}
```

### Claude Code

Em `.mcp.json`:

```json
{
  "mcpServers": {
    "asaas": {
      "type": "http",
      "url": "https://docs.asaas.com/mcp",
      "headers": {
        "Authorization": "Bearer COLE_O_VALOR_AQUI"
      }
    }
  }
}
```

### OpenCode

Em `opencode.json ou opencode.jsonc`:

```json
{
  "mcp": {
    "asaas": {
      "type": "remote",
      "url": "https://docs.asaas.com/mcp",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer COLE_O_VALOR_AQUI"
      }
    }
  }
}
```

Ou, no Claude Code, por comando:

```bash
claude mcp add --transport http asaas https://docs.asaas.com/mcp --header 'Authorization: Bearer COLE_O_VALOR_AQUI'
```

## Cabeçalhos

Requer: `Authorization`
