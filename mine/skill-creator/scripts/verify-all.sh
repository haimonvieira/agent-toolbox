#!/bin/sh
# verify-all.sh — Verificação completa do skill-creator e da skill de exemplo.
#
# Roda a partir do próprio repositório: testa mine/skill-creator e
# mine/incident-response. Não depende de nenhum cliente MCP instalado.
#
# Uso:
#   ./verify-all.sh
#   SKILLS_ROOT=/caminho/das/skills ./verify-all.sh
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SC="$(cd "$SCRIPT_DIR/.." && pwd)"                 # .../mine/skill-creator
SKILLS="${SKILLS_ROOT:-$(cd "$SC/.." && pwd)}"     # .../mine
TMP="$(mktemp -d)"
PASS=0
FAIL=0
OUT="$TMP/out"

trap 'rm -rf "$TMP"' EXIT

check() {
    desc="$1"; shift
    if "$@" >"$OUT" 2>&1; then
        echo "  ok     $desc"
        PASS=$((PASS + 1))
    else
        echo "  FALHA  $desc"
        sed 's/^/         /' "$OUT" | head -6
        FAIL=$((FAIL + 1))
    fi
}

echo "=========================================="
echo " verify-all — skill-creator"
echo " skills: $SKILLS"
echo "=========================================="
echo

echo "-- 1. Validação estrutural (skill-validate.py) --"
for s in skill-creator incident-response; do
    [ -d "$SKILLS/$s" ] || { echo "  pulado $s (não encontrada)"; continue; }
    check "$s passa em --strict" env SKILLS_ROOT="$SKILLS" python3 "$SC/scripts/skill-validate.py" "$SKILLS/$s" --strict
done
echo

echo "-- 2. Conformidade com a spec do Claude (quick_validate.py) --"
for s in skill-creator incident-response; do
    [ -d "$SKILLS/$s" ] || continue
    check "$s conforme à spec" python3 "$SC/scripts/quick_validate.py" "$SKILLS/$s"
done
echo

echo "-- 3. Testes automatizados (skill-test.py) --"
[ -d "$SKILLS/incident-response" ] && \
    check "incident-response: todos os testes" python3 "$SC/scripts/skill-test.py" "$SKILLS/incident-response"
echo

echo "-- 4. Servidor MCP (test-server.py) --"
check "skill-server.py responde" python3 "$SC/mcp/test-server.py"
echo

echo "-- 5. Empacotamento (package_skill.py) --"
DIST="$TMP/dist"
for s in skill-creator incident-response; do
    [ -d "$SKILLS/$s" ] && check "$s empacota" python3 "$SC/scripts/package_skill.py" "$SKILLS/$s" "$DIST"
done
check "arquivo .skill gerado" test -f "$DIST/skill-creator.skill"
echo

echo "-- 6. Scaffold gera skill válida --"
rm -rf "$SKILLS/verify-tmp-skill"
check "scaffold executa" env SKILLS_DIR="$SKILLS" \
    sh "$SC/scripts/skill-scaffold.sh" verify-tmp-skill \
    "Skill temporaria usada para verificar o fluxo completo de scaffold e validacao."
check "skill gerada passa na spec" python3 "$SC/scripts/quick_validate.py" "$SKILLS/verify-tmp-skill"
check "skill gerada passa no estrutural" env SKILLS_ROOT="$SKILLS" python3 "$SC/scripts/skill-validate.py" "$SKILLS/verify-tmp-skill"
rm -rf "$SKILLS/verify-tmp-skill"
echo

echo "-- 7. Handshake MCP (JSON-RPC direto) --"
check "initialize responde com serverInfo" sh -c '
    printf "%s\n" "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{}}" \
      | python3 "'"$SC"'/mcp/skill-server.py" | grep -q "skill-creator-server"'
check "tools/list devolve 7 ferramentas" sh -c '
    printf "%s\n" "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\"}" \
      | python3 "'"$SC"'/mcp/skill-server.py" \
      | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if len(d[\"result\"][\"tools\"])==7 else 1)"'
echo

echo "-- 8. Limite do corpo (< 500 linhas) --"
for s in skill-creator incident-response; do
    f="$SKILLS/$s/SKILL.md"
    [ -f "$f" ] || continue
    n=$(wc -l < "$f")
    if [ "$n" -le 500 ]; then
        echo "  ok     $s: $n linhas"
        PASS=$((PASS + 1))
    else
        echo "  FALHA  $s: $n linhas (acima de 500)"
        FAIL=$((FAIL + 1))
    fi
done
echo

echo "=========================================="
echo " RESULTADO: $PASS passou, $FAIL falhou"
echo "=========================================="
[ "$FAIL" -eq 0 ] || exit 1
exit 0
