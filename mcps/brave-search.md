# brave-search

Servidor MCP via stdio. Estado no ambiente de origem: ativo.

## Configurar

A mesma configuração nos três formatos. Troque `COLE_O_VALOR_AQUI` pelo valor real e mantenha a credencial fora do repositório.

### omp

Em `.omp/mcp.json`:

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "COLE_O_VALOR_AQUI"
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
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "COLE_O_VALOR_AQUI"
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
    "brave-search": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "enabled": true,
      "environment": {
        "BRAVE_API_KEY": "COLE_O_VALOR_AQUI"
      }
    }
  }
}
```

Ou, no Claude Code, por comando:

```bash
claude mcp add --env BRAVE_API_KEY=COLE_O_VALOR_AQUI brave-search -- npx -y @modelcontextprotocol/server-brave-search
```

## Variáveis de ambiente

O servidor espera estas variáveis. Os valores não estão neste repositório:

- `BRAVE_API_KEY`
