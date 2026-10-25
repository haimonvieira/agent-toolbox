# firecrawl-mcp

Servidor MCP via stdio. Estado no ambiente de origem: ativo.

## Configurar

A mesma configuração nos três formatos. Troque `COLE_O_VALOR_AQUI` pelo valor real e mantenha a credencial fora do repositório.

### omp

Em `.omp/mcp.json`:

```json
{
  "mcpServers": {
    "firecrawl-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "firecrawl-mcp"
      ],
      "env": {
        "FIRECRAWL_API_KEY": "COLE_O_VALOR_AQUI"
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
    "firecrawl-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "firecrawl-mcp"
      ],
      "env": {
        "FIRECRAWL_API_KEY": "COLE_O_VALOR_AQUI"
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
    "firecrawl-mcp": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "firecrawl-mcp"
      ],
      "enabled": true,
      "environment": {
        "FIRECRAWL_API_KEY": "COLE_O_VALOR_AQUI"
      }
    }
  }
}
```

Ou, no Claude Code, por comando:

```bash
claude mcp add --env FIRECRAWL_API_KEY=COLE_O_VALOR_AQUI firecrawl-mcp -- npx -y firecrawl-mcp
```

## Variáveis de ambiente

O servidor espera estas variáveis. Os valores não estão neste repositório:

- `FIRECRAWL_API_KEY`
