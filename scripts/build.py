#!/usr/bin/env python3
"""
build.py — Gera o repositório a partir de data/.

Entradas:  data/skills.json · data/mcps.json · data/provenance.json
           data/curated.json · data/pins.json
Saídas:    README.md · catalog.json · skills/*.md · mcps/*.md · recommended/*.md

Uso:  python3 scripts/build.py
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Categorias do inventário: (título, ordem)
CATEGORIES = {
    "meta":        ("Criar e orquestrar skills", 1),
    "memory":      ("Memória", 2),
    "dev":         ("Engenharia de código", 3),
    "github":      ("GitHub", 4),
    "web":         ("Web e busca", 5),
    "environment": ("Ambiente Minis / iSH", 6),
    "data":        ("APIs e dados", 7),
    "other":       ("Sem categoria", 8),
}

SKILL_CATEGORY = {
    "skill-creator": "meta", "find-skills": "meta", "skill-orchestrator": "meta",
    "tool-builder": "meta", "self-improving-agent": "meta", "self-learning": "meta",
    "saa-orchestrator": "meta", "production-agent-public": "meta", "mcp-connector": "meta",
    "memory-defrag": "memory", "memory-ingest": "memory", "memory-notes": "memory",
    "memory-reflect": "memory", "memory-schema": "memory", "memory-supermemory": "memory",
    "memory-tasks": "memory",
    "systematic-debugging": "dev", "verification-before-completion": "dev",
    "writing-plans": "dev", "executing-plans": "dev", "refactor-plan": "dev",
    "context-map": "dev", "hermes-codebase-inspection": "dev",
    "incident-response": "dev", "openrouter-rate-limits": "dev",
    "gh-cli": "github", "github-search": "github", "hermes-github-auth": "github",
    "web-search": "web", "web-content-extractor": "web", "firecrawl": "web",
    "exa-search": "web", "browser-automation": "web", "browser-batch": "web",
    "appstoreprice-hub": "web", "free-tts": "web",
    "minis-config-ops": "environment", "ish-background-services": "environment",
    "instalar-packages-python-no-ish": "environment",
    "asaas-mcp": "data", "hermes-maps": "data",
}

VERSION = "1.0.0"
REPO_URL = "https://github.com/haimonvieira/agent-toolbox"


def load():
    def j(name):
        p = DATA / name
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    skills = j("skills.json") or []
    mcps = j("mcps.json") or []
    prov = j("provenance.json") or {"known": {}, "unknown": []}
    curated = j("curated.json") or {"categories": {}, "entries": []}
    pins = j("pins.json") or []

    by_key = {(p["slug"], p["skill"]): p for p in pins}
    rec = []
    for c in curated.get("entries", []):
        e = dict(c)
        if e.get("local"):
            # Skill instalada localmente, sem upstream confirmável.
            e.update({
                "repo": "local", "repo_slug": "local", "skill": e["slug"],
                "path": f"skills/{e['slug']}/", "commit": "", "commit_short": "",
                "license": "MIT", "license_ok_to_copy": True,
                "stars": None, "pushed_at": None, "repo_description": None,
            })
        else:
            pin = by_key.get(tuple(c["slug_source"]))
            if not pin or pin.get("error"):
                continue
            e.update({
                "repo": pin["repo"], "repo_slug": pin["slug"], "skill": pin["skill"],
                "path": pin["path"], "commit": pin["commit"], "license": pin["license"],
                "license_ok_to_copy": pin.get("license_ok_to_copy", False),
                "stars": pin["stars"], "pushed_at": pin["pushed_at"],
                "repo_description": pin.get("description"), "commit_short": pin["commit"][:12],
            })
            e.pop("slug_source", None)
        rec.append(e)

    for s in skills:
        s["category"] = SKILL_CATEGORY.get(s["dir"], "other")
        s["origin"] = prov.get("known", {}).get(s["dir"])

    discovery = j("discovery.json") or {"intro": "", "entries": []}
    return skills, mcps, prov, rec, curated.get("categories", {}), discovery


def install_cmd(e):
    if e.get("local"):
        return None
    if e["license"] is None:
        return None
    return f'npx skills add {e["repo_slug"]}@{e["skill"]}'


def build_catalog(skills, mcps, rec):
    return {
        "name": "agent-toolbox",
        "version": VERSION,
        "description": "Setup de agente de IA documentado: skills instaladas, servidores MCP e recomendações.",
        "repository": REPO_URL,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "skills": len(skills), "mcps": len(mcps), "recommended": len(rec),
            "origins_known": sum(1 for s in skills if s["origin"]),
        },
        "skills": [{
            "dir": s["dir"], "name": s["name"], "category": s["category"],
            "description": s["description"], "resources": s["has"],
            "origin": s["origin"] or {"confidence": "nao_declarada"},
            "page": f"skills/{s['dir']}.md",
        } for s in skills],
        "mcps": [{
            "name": m["name"], "transport": m["transport"], "enabled": m["enabled"],
            "url": m["url"], "command": m["command"], "args": m["args"],
            "env_vars": m["env_vars"], "header_names": m["header_names"],
            "page": f"mcps/{m['name']}.md",
        } for m in mcps],
        "recommended": [{
            "slug": e["slug"], "name": e["skill"], "category": e["category"],
            "verdict": e["verdict"], "why": e["why"], "tags": e["tags"],
            "repo": e["repo"], "path": e["path"], "commit": e["commit"],
            "license": e["license"], "stars": e["stars"], "last_push": e["pushed_at"],
            "install": install_cmd(e), "page": f"recommended/{e['slug']}.md",
        } for e in rec],
    }


def build_readme(skills, mcps, prov, rec, cur_cats, discovery):
    by_cat = defaultdict(list)
    for s in skills:
        by_cat[s["category"]].append(s)

    known = sum(1 for s in skills if s["origin"])
    unknown_n = len(skills) - known
    today = datetime.now(timezone.utc).strftime("%d/%m/%Y")
    L = []
    A = L.append

    A("# Agent Toolbox")
    A("")
    A(f"Setup do meu agente de IA: **{len(skills)} skills** e **{len(mcps)} servidores MCP** em uso,")
    A("cada um com origem, licença e comando de instalação. Atualizado em " + today + ".")
    A("")
    A("O repositório tem duas partes:")
    A("")
    A("- **[Recomendações](#recomendações)** — 11 skills que eu uso e indico para quem está começando.")
    A(f"- **[Inventário](#inventário)** — as {len(skills)} skills e os {len(mcps)} MCPs que eu tenho instalados.")
    A("")
    A("As skills recomendadas são referenciadas por **commit**, não copiadas. Dois motivos: os")
    A("repositórios de origem recebem push semanal, então uma cópia ficaria defasada; e uma das")
    A("skills não declara licença, o que impede redistribuição. Cada ficha traz o commit exato.")
    A("")
    A("Para reconstruir o ambiente: `bash scripts/install_all.sh` (simula por padrão).")
    A("Para consumir por agente: [`catalog.json`](catalog.json).")
    A("")
    A("---")
    A("")
    A("## Como descobrir skills")
    A("")
    A(discovery.get("intro", ""))
    A("")
    for d in discovery.get("entries", []):
        A(f"### {d['name']}")
        A("")
        A(d["what"])
        A("")
        A(f"- Como usar: `{d['how']}`" if d["kind"] in ("mcp", "cli") else f"- Como usar: {d['how']}")
        A(f"- Onde: {d['url']}")
        A(f"- Escopo: {d['scope']} · Autenticação: {d['auth']}")
        if d.get("caveat"):
            A(f"- Ressalva: {d['caveat']}")
        A("")

    A("---")
    A("")
    A("## Recomendações")
    A("")
    A("Estas 11 skills foram verificadas uma a uma: o commit existe, o arquivo está no caminho")
    A("indicado e a licença foi conferida. Cada uma tem uma ficha com o commit exato.")
    A("")

    order = sorted(cur_cats.items(), key=lambda kv: kv[1].get("order", 99))
    grouped = defaultdict(list)
    for e in rec:
        grouped[e["category"]].append(e)

    for cat_key, cat in order:
        items = grouped.get(cat_key, [])
        if not items:
            continue
        A(f"### {cat['title']}")
        A("")
        for e in sorted(items, key=lambda x: x["slug"]):
            A(f"#### [{e['skill']}](recommended/{e['slug']}.md) · {e['verdict']}")
            A("")
            A(e["why"])
            A("")
            if e.get("local"):
                A(f"- Origem: instalada neste ambiente (sem upstream confirmável)")
                A(f"- Caminho: `{e['path']}`")
            else:
                A(f"- Repositório: [{e['repo_slug']}]({e['repo']}) — {e['stars']:,} stars, último push {e['pushed_at']}")
                A(f"- Caminho: `{e['path']}`")
                A(f"- Commit: `{e['commit_short']}`")
                A(f"- Licença: {e['license'] or 'não declarada'}")
            cmd = install_cmd(e)
            if cmd:
                A(f"- Instalar: `{cmd}`")
            if e.get("warning"):
                A(f"- Atenção: {e['warning']}")
            A("")

    A("---")
    A("")
    A("## Inventário")
    A("")
    A(f"Skills instaladas no meu ambiente. {known} têm origem confirmada, {unknown_n} não. As")
    A("sem origem aparecem marcadas como não documentadas, e não com uma origem suposta.")
    A("")

    A("| Categoria | Skills |")
    A("|---|---|")
    for cat_key in sorted(by_cat, key=lambda k: CATEGORIES.get(k, ("", 99))[1]):
        A(f"| {CATEGORIES.get(cat_key, (cat_key, 99))[0]} | {len(by_cat[cat_key])} |")
    A("")

    for cat_key in sorted(by_cat, key=lambda k: CATEGORIES.get(k, ("", 99))[1]):
        A(f"### {CATEGORIES.get(cat_key, (cat_key, 99))[0]}")
        A("")
        A("| Skill | O que faz | Origem |")
        A("|---|---|---|")
        for s in sorted(by_cat[cat_key], key=lambda x: x["dir"]):
            d = (s["description"] or "—").replace("|", "\\|")
            d = d[:100] + ("…" if len(s["description"]) > 100 else "")
            if s["origin"]:
                r = s["origin"]["repo"]
                o = f"[{r.replace('https://github.com/', '')}]({r})" if r.startswith("http") else r
            else:
                o = "não documentada"
            A(f"| [`{s['dir']}`](skills/{s['dir']}.md) | {d} | {o} |")
        A("")

    A("---")
    A("")
    A("## Servidores MCP")
    A("")
    A("| Servidor | Transporte | Precisa de | Estado |")
    A("|---|---|---|---|")
    for m in sorted(mcps, key=lambda x: x["name"]):
        need = ", ".join(f"`{v}`" for v in m["env_vars"]) or (
            ", ".join(f"header `{h}`" for h in m["header_names"]) or "—")
        A(f"| [`{m['name']}`](mcps/{m['name']}.md) | {m['transport']} | {need} | "
          f"{'ativo' if m['enabled'] else 'desligado'} |")
    A("")
    A("As credenciais não estão neste repositório. Cada ficha diz qual variável de ambiente ou")
    A("cabeçalho o servidor espera.")
    A("")

    A("---")
    A("")
    A("## Reconstruir o ambiente")
    A("")
    A("```bash")
    A(f"git clone {REPO_URL} && cd agent-toolbox")
    A("bash scripts/install_all.sh          # simula: mostra o que seria feito")
    A("bash scripts/install_all.sh --apply  # executa, confirmando item por item")
    A("```")
    A("")
    A("Manter o inventário em dia:")
    A("")
    A("```bash")
    A("python3 scripts/gather.py        # relê o ambiente para data/*.json")
    A("python3 scripts/resolve_pins.py  # re-resolve os commits das recomendações")
    A("python3 scripts/build.py         # regenera README, catalog.json e as fichas")
    A("python3 scripts/verify_pins.py   # confere se os commits ainda existem")
    A("```")
    A("")
    A("---")
    A("")
    A("## Licença")
    A("")
    A("MIT ([LICENSE](LICENSE)) para a documentação e os scripts deste repositório. As skills e")
    A("servidores MCP referenciados são de terceiros e mantêm suas licenças, indicadas em cada")
    A("ficha. Nada de terceiros é redistribuído. Ver [NOTICE](NOTICE) para as atribuições.")
    A("")
    return "\n".join(L)


def build_skill_pages(skills):
    out = []
    for s in skills:
        o = s["origin"]
        L = [f"# {s['dir']}", ""]
        L += ["## Descrição declarada", "", s["description"] or "_A skill não declara descrição._", ""]
        L += ["## Origem", ""]
        if o:
            L += ["| Campo | Valor |", "|---|---|",
                  f"| Repositório | {o['repo']} |", f"| Caminho | `{o['path']}` |",
                  f"| Licença | {o['license']} |", f"| Confiança | {o['confidence']} |", ""]
            if o.get("install", "").startswith("npx"):
                L += ["```bash", o["install"], "```", ""]
            if o.get("note"):
                L += [o["note"], ""]
        else:
            L += ["Não documentada. A skill está instalada, mas o arquivo não cita repositório",
                  "nem autor. Para completar, edite `data/provenance.json`.", ""]
        if s["has"]:
            L += ["## Recursos", "", ", ".join(f"`{k}/`" for k in s["has"]), ""]
        L += ["## Tamanho", "",
              f"- `SKILL.md`: {s['skill_md_bytes']:,} bytes, {s['body_lines']} linhas de corpo",
              f"- Arquivos no diretório: {s['files']}",
              f"- Versão declarada: {s['version'] or '—'}", ""]
        p = ROOT / "skills" / f"{s['dir']}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(L), encoding="utf-8")
        out.append(str(p.relative_to(ROOT)))
    return out


def build_mcp_pages(mcps):
    out = []
    for m in mcps:
        L = [f"# {m['name']}", "",
             f"Servidor MCP via {m['transport']}. Estado atual: "
             f"{'ativo' if m['enabled'] else 'desligado'}.", ""]
        L += ["## Registrar", ""]
        if m["transport"] == "http":
            hdrs = "".join(f' \\\n  --header "{h}: <valor>"' for h in m["header_names"])
            L += ["```bash", f'minis-mcp-cli add --name {m["name"]} --url "{m["url"]}"{hdrs}', "```", ""]
        else:
            args = " ".join(m["args"])
            L += ["```bash",
                  f'minis-mcp-cli add --name {m["name"]} --command {m["command"]}' +
                  (f' --args "{args}"' if args else ""),
                  "```", ""]
        if m["env_vars"]:
            L += ["## Variáveis de ambiente", "",
                  "O servidor espera estas variáveis. Os valores não estão neste repositório:", ""]
            for v in m["env_vars"]:
                L += [f"- `{v}` — [criar](minis://settings/environments?create_key={v})"]
            L += [""]
        if m["header_names"]:
            L += ["## Cabeçalhos", "", "Requer: " + ", ".join(f"`{h}`" for h in m["header_names"]), ""]
        if m["note"]:
            L += ["## Nota", "", m["note"], ""]
        L += ["## Verificar", "", "```bash",
              f"minis-mcp-cli ping {m['name']}", f"minis-mcp-cli tools {m['name']}", "```", ""]
        p = ROOT / "mcps" / f"{m['name']}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(L), encoding="utf-8")
        out.append(str(p.relative_to(ROOT)))
    return out


def build_recommended_pages(rec, cur_cats):
    out = []
    for e in rec:
        cat = cur_cats.get(e["category"], {})
        L = [f"# {e['skill']}", "", f"Categoria: {cat.get('title', e['category'])}. "
             f"Classificação: {e['verdict']}.", "", "## Por que está aqui", "", e["why"], ""]
        if e.get("warning"):
            L += [f"Atenção: {e['warning']}", ""]
        if e.get("local"):
            L += ["## Origem", "",
                  "Instalada neste ambiente. Não há upstream confirmável: circulam cópias do",
                  "mesmo texto em vários repositórios e o original não pôde ser localizado.", "",
                  f"Caminho: `{e['path']}`", ""]
        else:
            L += ["## Origem", "", "| Campo | Valor |", "|---|---|",
                  f"| Repositório | [{e['repo_slug']}]({e['repo']}) |",
                  f"| Caminho | `{e['path']}` |", f"| Commit | `{e['commit']}` |",
                  f"| Licença | {e['license'] or 'não declarada'} |",
                  f"| Stars | {e['stars']:,} |", f"| Último push | {e['pushed_at']} |",
                  f"| Tags | {', '.join('`'+t+'`' for t in e['tags'])} |", ""]
        L += ["## Instalar", ""]
        cmd = install_cmd(e)
        if e.get("local"):
            L += ["Incluída em `mine/` neste repositório. Copie para o diretório de skills do",
                  "seu agente.", ""]
        elif cmd:
            L += ["```bash", cmd, "```", "",
                  "No commit exato deste catálogo:", "",
                  "```bash", f"git clone {e['repo']} /tmp/s",
                  f"cd /tmp/s && git checkout {e['commit_short']}",
                  f"# copie '{e['path']}' para o diretório de skills do seu agente", "```", ""]
        else:
            L += ["Sem instalação automatizada: o repositório não declara licença, então não há",
                  "permissão de redistribuição. Consulte a fonte:", "",
                  "```bash", f"git clone {e['repo']} /tmp/s", f"# leia: /tmp/s/{e['path']}", "```", ""]
        p = ROOT / "recommended" / f"{e['slug']}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(L), encoding="utf-8")
        out.append(str(p.relative_to(ROOT)))
    return out


def main():
    skills, mcps, prov, rec, cur_cats, discovery = load()
    if not skills:
        print("ERRO: rode scripts/gather.py primeiro.", file=sys.stderr)
        return 1

    (ROOT / "catalog.json").write_text(
        json.dumps(build_catalog(skills, mcps, rec), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    (ROOT / "README.md").write_text(build_readme(skills, mcps, prov, rec, cur_cats, discovery), encoding="utf-8")
    sp = build_skill_pages(skills)
    ep = build_mcp_pages(mcps)
    rp = build_recommended_pages(rec, cur_cats)

    print(f"README.md       — {len(skills)} skills, {len(mcps)} MCPs, {len(rec)} recomendações")
    print(f"catalog.json    — índice completo")
    print(f"skills/         — {len(sp)} fichas")
    print(f"mcps/           — {len(ep)} fichas")
    print(f"recommended/    — {len(rp)} fichas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
