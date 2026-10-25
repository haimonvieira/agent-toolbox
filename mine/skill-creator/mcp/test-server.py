#!/usr/bin/env python3
"""Testa o servidor MCP skill-server.py via JSON-RPC over stdio."""
import json
import subprocess
import sys

SERVER = "/var/minis/skills/skill-creator/mcp/skill-server.py"


def run_raw(requests):
    payload = "\n".join(json.dumps(r) for r in requests) + "\n"
    proc = subprocess.run(
        [sys.executable, SERVER],
        input=payload, capture_output=True, text=True, timeout=120,
    )
    out = []
    for line in proc.stdout.strip().splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                out.append({"parse_error": line[:200]})
    return out, proc.stderr


def inner(response):
    """Extrai e parseia o payload aninhado em result.content[0].text."""
    try:
        text = response["result"]["content"][0]["text"]
        return json.loads(text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return {}


def main():
    # garante estado limpo antes do teste
    subprocess.run(["rm", "-rf", "/var/minis/skills/mcp-test-skill"])

    reqs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "list_skills", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "create_skill",
                    "arguments": {"name": "mcp-test-skill",
                                  "description": ("Skill de teste para validar o servidor MCP de criacao de skills. "
                                                  "Use quando precisar testar o fluxo completo de scaffold e "
                                                  "validacao automatizada de skills no ambiente Minis.")}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
         "params": {"name": "validate_skill", "arguments": {"name": "mcp-test-skill"}}},
        {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
         "params": {"name": "read_skill", "arguments": {"name": "mcp-test-skill", "max_chars": 500}}},
        {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
         "params": {"name": "update_skill", "arguments": {"name": "mcp-test-skill", "version": "1.1.0"}}},
        {"jsonrpc": "2.0", "id": 8, "method": "tools/call",
         "params": {"name": "validate_skill", "arguments": {"name": "skill-creator"}}},
        {"jsonrpc": "2.0", "id": 9, "method": "tools/call",
         "params": {"name": "test_skill", "arguments": {"name": "incident-response"}}},
        {"jsonrpc": "2.0", "id": 10, "method": "tools/call",
         "params": {"name": "get_skill_template", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 11, "method": "tools/call",
         "params": {"name": "nao_existe", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 12, "method": "tools/call",
         "params": {"name": "create_skill", "arguments": {"name": "Nome Invalido!!", "description": "x"}}},
    ]

    responses, stderr = run_raw(reqs)
    by_id = {r.get("id"): r for r in responses}

    checks = []

    # 1. initialize
    info = by_id.get(1, {}).get("result", {}).get("serverInfo", {})
    checks.append(("initialize devolve serverInfo", info.get("name") == "skill-creator-server"))

    # 2. tools/list
    tools = by_id.get(2, {}).get("result", {}).get("tools", [])
    names = {t["name"] for t in tools}
    expected = {"create_skill", "validate_skill", "test_skill", "list_skills",
                "read_skill", "get_skill_template", "update_skill"}
    checks.append((f"tools/list tem as 7 ferramentas ({len(tools)})", names == expected))
    checks.append(("cada ferramenta tem inputSchema",
                   all("inputSchema" in t and t["inputSchema"].get("type") == "object" for t in tools)))

    # 3. list_skills
    ls = inner(by_id.get(3, {}))
    checks.append(("list_skills marca ok e conta skills", ls.get("ok") is True and ls.get("count", 0) >= 2))

    # 4. create_skill
    cs = inner(by_id.get(4, {}))
    checks.append(("create_skill cria estrutura", cs.get("ok") is True and "SKILL.md" in cs.get("created", [])))
    checks.append(("create_skill retorna next_steps", len(cs.get("next_steps", [])) >= 4))

    # 5. validate_skill
    vs = inner(by_id.get(5, {}))
    checks.append(("validate_skill aprova skill nova", vs.get("passed") is True))

    # 6. read_skill
    rs = inner(by_id.get(6, {}))
    checks.append(("read_skill devolve conteúdo", rs.get("ok") is True and "name: mcp-test-skill" in rs.get("content", "")))

    # 7. update_skill
    us = inner(by_id.get(7, {}))
    checks.append(("update_skill altera versão", us.get("ok") is True and "version" in us.get("changed", [])))
    # confirma que persistiu
    r2, _ = run_raw([{"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                      "params": {"name": "read_skill", "arguments": {"name": "mcp-test-skill", "max_chars": 2000}}}])
    checks.append(("versão 1.1.0 persistida", 'version: "1.1.0"' in inner(r2[0]).get("content", "")))

    # 8. skill-creator se auto-valida
    vc = inner(by_id.get(8, {}))
    checks.append(("skill-creator passa na validação", vc.get("passed") is True))

    # 9. test_skill
    ts = inner(by_id.get(9, {}))
    checks.append(("test_skill roda incident-response", ts.get("ok") is True and "5" in ts.get("output", "")))

    # 10. template
    tp = inner(by_id.get(10, {}))
    checks.append(("get_skill_template devolve conteúdo", tp.get("ok") is True and "nome-da-skill" in tp.get("content", "")))

    # 11. ferramenta inexistente
    checks.append(("ferramenta inexistente → erro JSON-RPC", "error" in by_id.get(11, {})))

    # 12. nome inválido rejeitado
    ci = inner(by_id.get(12, {}))
    checks.append(("nome inválido rejeitado", ci.get("ok") is False))

    print("=== Testes do servidor MCP skill-creator ===")
    ok = 0
    for name, passed in checks:
        print(f"  {'✅' if passed else '❌'} {name}")
        ok += 1 if passed else 0
    print(f"\n{ok}/{len(checks)} testes passaram")

    if stderr.strip():
        print("\n--- stderr ---")
        print(stderr[:800])

    subprocess.run(["rm", "-rf", "/var/minis/skills/mcp-test-skill"])
    return 0 if ok == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())