#!/usr/bin/env bash
# install_all.sh — Reconstrói o ambiente a partir deste repositório.
#
# Padrão (simulação): mostra o que seria feito, sem alterar nada.
# Com --apply: executa, pedindo confirmação item por item.
#
# Uso:
#   bash scripts/install_all.sh                       simula (padrão)
#   bash scripts/install_all.sh --apply               executa, confirmando item por item
#   bash scripts/install_all.sh --apply --yes         executa sem pedir confirmação
#   bash scripts/install_all.sh --apply --only-mcps   só os servidores MCP
#   bash scripts/install_all.sh --apply --only-skills só as skills

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CATALOG="$ROOT/catalog.json"
APPLY=0
YES=0
ONLY=""

for arg in "$@"; do
    case "$arg" in
        --apply) APPLY=1 ;;
        --yes|-y) YES=1; APPLY=1 ;;
        --only-mcps) ONLY="mcps" ;;
        --only-skills) ONLY="skills" ;;
        -h|--help) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    esac
done

[ -f "$CATALOG" ] || { echo "ERRO: catalog.json não encontrado. Rode scripts/build.py." >&2; exit 2; }
command -v python3 >/dev/null || { echo "ERRO: python3 é necessário." >&2; exit 2; }

PLACEHOLDER="COLE_O_VALOR_AQUI"

confirm() {
    [ "$APPLY" -eq 0 ] && return 1
    [ "$YES" -eq 1 ] && return 0
    printf "    executar? [s/N] "
    read -r ans </dev/tty 2>/dev/null || {
        echo "    (sem terminal interativo: pulando. use --yes para aprovar tudo)"
        return 1
    }
    case "$ans" in [sSyY]*) return 0 ;; *) return 1 ;; esac
}

# Mostra o comando de forma segura para copiar e colar.
show_cmd() {
    python3 -c 'import shlex,sys; print("    $ " + " ".join(shlex.quote(a) for a in sys.argv[1:]))' "$@"
}

echo "=============================================================="
echo " agent-toolbox — reconstrução do ambiente"
if [ "$APPLY" -eq 0 ]; then
    echo " modo simulação: nada será alterado. use --apply para executar."
else
    if [ "$YES" -eq 1 ]; then
        echo " modo execução: --yes, todas as confirmações aprovadas automaticamente."
    else
        echo " modo execução: confirmação pedida item por item."
    fi
fi
echo "=============================================================="
echo

# ---------------------------------------------------------------- MCPs
if [ "$ONLY" != "skills" ]; then
    echo "--- servidores MCP ---"
    # Cada linha: nome \t JSON-array-de-argumentos \t variáveis-de-ambiente
    python3 - "$CATALOG" "$PLACEHOLDER" <<'PY' > /tmp/_mcp_plan
import json, sys
cat, ph = sys.argv[1], sys.argv[2]
c = json.load(open(cat))
for m in sorted(c["mcps"], key=lambda x: x["name"]):
    args = []
    if m["transport"] == "http":
        args += ["--url", m["url"] or ""]
        for h in m["header_names"]:
            args += ["--header", f"{h}: Bearer {ph}"]
    else:
        args += ["--command", m["command"] or ""]
        if m["args"]:
            args += ["--args", " ".join(m["args"])]
    print(f'{m["name"]}\t{json.dumps(args)}\t{",".join(m["env_vars"])}')
PY

    while IFS=$'\t' read -r name args_json envs; do
        [ -z "$name" ] && continue
        # iSH não tem /dev/fd: process substitution não funciona.
        # Por isso os argumentos passam por um arquivo temporário.
        printf '%s' "$args_json" > /tmp/_atb_args.json
        python3 -c 'import json,sys; [print(a) for a in json.loads(open(sys.argv[1]).read())]' /tmp/_atb_args.json > /tmp/_atb_args.txt
        mapfile -t ARGS < /tmp/_atb_args.txt

        echo "  $name"
        if [ -n "$envs" ]; then
            echo "      variáveis necessárias: $envs"
            echo "      crie as variáveis antes: os valores não estão neste repositório"
        fi
        show_cmd minis-mcp-cli add --name "$name" "${ARGS[@]}"
        if confirm "$name"; then
            minis-mcp-cli add --name "$name" "${ARGS[@]}"
        fi
        echo
    done < /tmp/_mcp_plan
    rm -f /tmp/_mcp_plan /tmp/_atb_args.json /tmp/_atb_args.txt
fi

# ---------------------------------------------------------------- Skills
if [ "$ONLY" != "mcps" ]; then
    echo "--- skills recomendadas ---"
    python3 - "$CATALOG" <<'PY' > /tmp/_skill_plan
import json, sys
c = json.load(open(sys.argv[1]))
for s in c["recommended"]:
    lic = s["license"] or ""
    print(f'{s["name"]}\t{s["repo"]}\t{s["commit"]}\t{s["path"]}\t{lic}\t{s["install"] or ""}')
PY

    while IFS=$'\t' read -r name repo commit path lic install; do
        [ -z "$name" ] && continue
        echo "  $name  (licença: ${lic:-não declarada})"
        if [ -z "$lic" ]; then
            echo "      sem licença declarada: não há instalação automatizada."
            echo "      consulte a fonte: $repo"
            echo
            continue
        fi
        show_cmd npx -y skills add "${install#npx skills add }"
        if confirm "$name"; then
            npx -y skills add "${install#npx skills add }"
        fi
        echo
    done < /tmp/_skill_plan
    rm -f /tmp/_skill_plan

    echo "--- skills autorais (incluídas neste repositório) ---"
    for d in mine/*/; do
        [ -d "$d" ] || continue
        n="$(basename "$d")"
        echo "  $n: copie $d para /var/minis/skills/$n"
    done
    echo
fi

echo "=============================================================="
if [ "$APPLY" -eq 0 ]; then
    echo " simulação concluída. nada foi alterado."
    echo " use --apply para executar."
else
    echo " concluído. valide com: minis-mcp-cli ping <servidor>"
fi
echo "=============================================================="
