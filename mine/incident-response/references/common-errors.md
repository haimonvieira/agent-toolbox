# Padrões de Erros Conhecidos

Este arquivo é consultado pelo agente durante a etapa de análise (passo 3 do fluxo)
para identificar se o erro já é um padrão documentado.

## Padrões por Categoria

### Infraestrutura / Conectividad

| Sintoma no log | Causa provável | Ação imediata |
|---|---|---|
| `Connection refused`, `Connection reset` | Serviço dependente indisponível | Verificar health check do serviço |
| `Connection timeout`, `timed out` | Lentidão ou timeout de rede | Aumentar timeout; verificar latência |
| `SSL handshake failed`, `certificate verify failed` | Certificado expirado ou inválido | Renovar certificado; verificar data do sistema |
| `DNS resolution failed` | DNS | Verificar configuração de DNS |

### Banco de Dados

| Sintoma no log | Causa provável | Ação imediata |
|---|---|---|
| `deadlock detected`, `deadlock` | Deadlock em transação | Revisar ordem de locks; retry automático |
| `Connection pool exhausted`, `pool exhausted` | Pool de conexões esgotado | Aumentar pool; investigar vazamento |
| `Query timeout`, `statement timeout` | Query lenta | Analisar EXPLAIN; adicionar índice |
| `syntax error at or near`, `SQLSyntaxError` | SQL inválido | Verificar deploy recente de migração |

### Aplicação

| Sintoma no log | Causa provável | Ação imediata |
|---|---|---|
| `OutOfMemoryError`, `Java heap space` | Vazamento de memória | Heap dump; aumentar heap (-Xmx) |
| `NullPointerException`, `NoneType`, `undefined is not` | Valor nulo não tratado | Revisar entrada; adicionar null check |
| `StackOverflowError` | Recursão infinita | Revisar lógica recursiva |
| `ArrayIndexOutOfBoundsException`, `IndexError` | Índice inválido | Validar limites de coleção |

### APIs / HTTP

| Sintoma no log | Causa provável | Ação imediata |
|---|---|---|
| `429 Too Many Requests`, `RateLimitExceeded` | Limite de quota | Implementar backoff; pedir aumento de quota |
| `500 Internal Server Error` | Erro no servidor upstream | Verificar logs do upstream |
| `502 Bad Gateway`, `503 Service Unavailable` | Gateway ou serviço caído | Check health; revisar deployment |
| `401 Unauthorized`, `auth failed` | Credencial inválida | Rotacionar API key; verificar scope |

### Sistema / Runtime

| Sintoma no log | Causa provável | Ação imediata |
|---|---|---|
| `No space left on device` | Disco cheio | Limpar logs; expandir volume |
| `Too many open files` | Limite de file descriptors | Aumentar ulimit; investigar vazamento |
| `SIGKILL`, `OOM killed` | Processo morto por memória | Investigar consumo de memória |
| `Permission denied`, `EACCES` | Permissão de arquivo | Verificar chmod/ownership |

## Como Usar

1. Cole o trecho de erro do log aqui e procure correspondência.
2. Se encontrar, reporte o padrão no diagnóstico com o link para a ação imediata.
3. Se não encontrar, marque como "padrão desconhecido" e aumente a incerteza no nível de confiança.
4. Erros que combinam múltiplos padrões geralmente indicam erro em cascata — o primeiro na linha do tempo é a causa raiz.

## Limitações

- Este arquivo contém padrões genéricos. Erros específicos do domínio devem ser documentados
  em `references/domain-errors.md` (crie se necessário).
- O script `scripts/parse_logs.py` já faz varredura automática dos padrões mais comuns.
  Use este arquivo para contexto adicional e ações de resposta.