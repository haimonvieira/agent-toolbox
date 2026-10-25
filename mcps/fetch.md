# fetch

Servidor MCP via stdio. Estado no ambiente de origem: desligado.

## Configurar

A mesma configuração nos três formatos.

### omp

Em `.omp/mcp.json`:

```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-fetch"
      ]
    }
  }
}
```

### Claude Code

Em `.mcp.json`:

```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-fetch"
      ]
    }
  }
}
```

### OpenCode

Em `opencode.json ou opencode.jsonc`:

```json
{
  "mcp": {
    "fetch": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "@modelcontextprotocol/server-fetch"
      ],
      "enabled": true
    }
  }
}
```

Ou, no Claude Code, por comando:

```bash
claude mcp add fetch -- npx -y @modelcontextprotocol/server-fetch
```
