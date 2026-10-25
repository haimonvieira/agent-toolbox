# omgskills

Servidor MCP via http. Estado no ambiente de origem: ativo.

## Configurar

A mesma configuração nos três formatos.

### omp

Em `.omp/mcp.json`:

```json
{
  "mcpServers": {
    "omgskills": {
      "type": "http",
      "url": "https://omgskills.com/mcp"
    }
  }
}
```

### Claude Code

Em `.mcp.json`:

```json
{
  "mcpServers": {
    "omgskills": {
      "type": "http",
      "url": "https://omgskills.com/mcp"
    }
  }
}
```

### OpenCode

Em `opencode.json ou opencode.jsonc`:

```json
{
  "mcp": {
    "omgskills": {
      "type": "remote",
      "url": "https://omgskills.com/mcp",
      "enabled": true
    }
  }
}
```

Ou, no Claude Code, por comando:

```bash
claude mcp add --transport http omgskills https://omgskills.com/mcp
```

## Nota

Catálogo público read-only de skills de agentes (55k+). Ferramentas: search_skills, get_skill, get_skills, list_trending, list_gold_basket, list_by_author. Instalável apenas quando pinned_install existe.
