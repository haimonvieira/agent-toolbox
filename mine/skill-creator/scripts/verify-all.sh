#!/bin/sh
# verify-all.sh — Verificação completa do ecossistema skill-creator.
# Uso: ./verify-all.sh
set -u

SC="/var/minis/skills/skill-creator"
PASS=0
FAIL=0

check() {
    # check <descrição> <comando...>
    desc="$1"; shift
    if "$@" >/tmp/vout 2>&1; then
        echo "  ✅ $desc"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $desc"
        sed 's/^/       /' /tmp/vout | head -6
        FAIL=$((FAIL + 1))
    fi
}

echo "=========================================="
echo " VERIFICAÇÃO COMPLETA — skill-creator"
echo "=========================================="
echo

echo "── 1. Validação estrutural (skill-validate.py) ──"
for s in skill-creator incident-response; do
    check "$s passa em --strict" python3 "$SC/scripts/skill-validate.py" "/var/minis/skills/$s" --strict
done
echo

echo "── 2. Conformidade com a spec do Claude (quick_validate.py) ──"
for s in skill-creator incident-response; do
    check "$s conforme à spec" python3 "$SC/scripts/quick_validate.py" "/var/minis/skills/$s"
done
echo

echo "── 3. Testes automatizados (skill-test.py) ──"
check "incident-response: 5/5 testes" python3 "$SC/scripts/skill-test.py" /var/minis/skills/incident-response
echo

echo "── 4. Servidor MCP (15 testes) ──"
check "skill-server.py: 15/15" python3 "$SC/mcp/test-server.py"
echo

echo "── 5. Empacotamento (package_skill.py) ──"
rm -rf /tmp/vdist
check "skill-creator empacota" python3 "$SC/scripts/package_skill.py" /var/minis/skills/skill-creator /tmp/vdist
check "incident-response empacota" python3 "$SC/scripts/package_skill.py" /var/minis/skills/incident-response /tmp/vdist
check "arquivo .skill gerado" test -f /tmp/vdist/skill-creator.skill
echo

echo "── 6. Scaffold gera skill válida ──"
rm -rf /var/minis/skills/verify-tmp-skill
check "scaffold executa" sh "$SC/scripts/skill-scaffold.sh" verify-tmp-skill "Skill temporaria de verificacao do fluxo completo de scaffold e validacao automatica de skills no ambiente Minis."
check "skill gerada é válida (spec)" python3 "$SC/scripts/quick_validate.py" /var/minis/skills/verify-tmp-skill
check "skill gerada é válida (estrutural)" python3 "$SC/scripts/skill-validate.py" /var/minis/skills/verify-tmp-skill
rm -rf /var/minis/skills/verify-tmp-skill
echo

echo "── 7. Servidor MCP registrado no cliente ──"
check "ping responde" minis-mcp-cli ping skill-creator
check "7 ferramentas listadas" sh -c "minis-mcp-cli tools skill-creator | grep -c create_skill"
echo

echo "── 8. Limites do corpo (< 500 linhas) ──"
for s in skill-creator incident-response; do
    n=$(wc -l < "/var/minis/skills/$s/SKILL.md")
    if [ "$n" -le 500 ]; then
        echo "  ✅ $s: $n linhas"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $s: $n linhas (acima de 500)"
        FAIL=$((FAIL + 1))
    fi
done
echo

echo "=========================================="
echo " RESULTADO: $PASS passou, $FAIL falhou"
echo "=========================================="
rm -rf /tmp/vout /tmp/vdist
[ "$FAIL" -eq 0 ] || exit 1
exit 0