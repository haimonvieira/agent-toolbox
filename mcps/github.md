# github

Servidor MCP via stdio. Estado no ambiente de origem: ativo.

## Configurar

A mesma configuração nos três formatos. Troque `COLE_O_VALOR_AQUI` pelo valor real e mantenha a credencial fora do repositório.

### omp

Em `.omp/mcp.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "COLE_O_VALOR_AQUI"
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
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "COLE_O_VALOR_AQUI"
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
    "github": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "enabled": true,
      "environment": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "COLE_O_VALOR_AQUI"
      }
    }
  }
}
```

Ou, no Claude Code, por comando:

```bash
claude mcp add --env GITHUB_PERSONAL_ACCESS_TOKEN=COLE_O_VALOR_AQUI github -- npx -y @modelcontextprotocol/server-github
```

## Variáveis de ambiente

O servidor espera estas variáveis. Os valores não estão neste repositório:

- `GITHUB_PERSONAL_ACCESS_TOKEN`
