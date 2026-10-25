# skill-creator

Servidor MCP via stdio. Estado no ambiente de origem: ativo.

## Configurar

A mesma configuração nos três formatos.

### omp

Em `.omp/mcp.json`:

```json
{
  "mcpServers": {
    "skill-creator": {
      "command": "python3",
      "args": [
        "$HOME/agent-toolbox/mine/skill-creator/mcp/skill-server.py"
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
    "skill-creator": {
      "command": "python3",
      "args": [
        "$HOME/agent-toolbox/mine/skill-creator/mcp/skill-server.py"
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
    "skill-creator": {
      "type": "local",
      "command": [
        "python3",
        "$HOME/agent-toolbox/mine/skill-creator/mcp/skill-server.py"
      ],
      "enabled": true
    }
  }
}
```

Ou, no Claude Code, por comando:

```bash
claude mcp add skill-creator -- python3 '$HOME/agent-toolbox/mine/skill-creator/mcp/skill-server.py'
```

## Nota

Servidor MCP para criar, validar, testar e gerir skills de agentes de IA
