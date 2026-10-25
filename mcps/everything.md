# everything

Servidor MCP via stdio. Estado no ambiente de origem: ativo.

## Configurar

A mesma configuração nos três formatos.

### omp

Em `.omp/mcp.json`:

```json
{
  "mcpServers": {
    "everything": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-everything"
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
    "everything": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-everything"
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
    "everything": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "@modelcontextprotocol/server-everything"
      ],
      "enabled": true
    }
  }
}
```

Ou, no Claude Code, por comando:

```bash
claude mcp add everything -- npx -y @modelcontextprotocol/server-everything
```
