# filesystem

Servidor MCP via stdio. Estado no ambiente de origem: ativo.

## Configurar

A mesma configuração nos três formatos.

### omp

Em `.omp/mcp.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "$HOME/agent-toolbox"
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
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "$HOME/agent-toolbox"
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
    "filesystem": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "$HOME/agent-toolbox"
      ],
      "enabled": true
    }
  }
}
```

Ou, no Claude Code, por comando:

```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem '$HOME/agent-toolbox'
```
