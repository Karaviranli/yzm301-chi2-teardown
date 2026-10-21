"""MCP ↔ CLI paritesi: aynı girdide aynı çıktı (bonus +15 şartı).

Her vektör hem CLI'ye (alt süreç, kara kutu) hem MCP sunucusuna (gerçek MCP
protokolü, süreç içi bellek taşıması) gönderilir; JSON çıktıları birebir aynı olmalı.
"""

import asyncio
import json
import os
import pathlib
import subprocess
import sys

import pytest

mcp = pytest.importorskip("mcp")

from powerchi.mcp_server import server  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]

VECTORS = [
    dict(mode="a-priori", w=0.3, alpha=0.05, power=0.8, df=1),
    dict(mode="a-priori", w=0.1, alpha=0.05, power=0.95, df=1),
    dict(mode="a-priori", w=0.3, alpha=0.05, power=0.95, df=5),
    dict(mode="a-priori", w=0.25, alpha=0.01, power=0.9, df=6),
    dict(mode="a-priori", w=3, alpha=0.05, power=0.8, df=1),
    dict(mode="a-priori", w=0.01, alpha=0.05, power=0.8, df=1),
    dict(mode="post-hoc", w=0.3, alpha=0.05, n=88, df=1),
    dict(mode="post-hoc", w=0.5, alpha=0.05, n=10, df=3),
    dict(mode="post-hoc", w=0, alpha=0.05, n=100, df=1),
    # geçersiz girdiler: ikisi de hata vermeli
    dict(mode="a-priori", w=0.3, alpha=0.05, power=0.05, df=1),
    dict(mode="a-priori", w=0, alpha=0.05, power=0.8, df=1),
    dict(mode="post-hoc", w=0.3, alpha=0.05, n=0, df=1),
]


def cli(v: dict) -> dict:
    args = ["--test", "chi2-contingency", "--mode", v["mode"], "--w", str(v["w"]), "--alpha", str(v["alpha"]),
            "--df", str(v["df"])]
    if "power" in v:
        args += ["--power", str(v["power"])]
    if "n" in v:
        args += ["--n", str(v["n"])]
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    p = subprocess.run([sys.executable, "-m", "powerchi", *args], capture_output=True, text=True, env=env)
    return json.loads(p.stdout)


def _payload(result) -> dict:
    sc = getattr(result, "structured_content", None) or getattr(result, "structuredContent", None)
    if sc:
        return sc.get("result", sc) if set(sc) == {"result"} else sc
    return json.loads(result.content[0].text)


async def _call_all(calls):
    out = []
    async with mcp.Client(server) as client:
        for name, args in calls:
            out.append(_payload(await client.call_tool(name, args)))
    return out


def mcp_calls(calls):
    return asyncio.run(_call_all(calls))


def test_tools_listed():
    async def go():
        async with mcp.Client(server) as c:
            return [t.name for t in (await c.list_tools()).tools]
    names = asyncio.run(go())
    assert {"chi2_contingency_power", "chi2_effect_size"} <= set(names)


def test_mcp_equals_cli():
    mcp_out = mcp_calls([("chi2_contingency_power", v) for v in VECTORS])
    for v, m in zip(VECTORS, mcp_out):
        c = cli(v)
        if "error" in c:
            assert "error" in m, (v, m)
            assert m["error"] == c["error"]
        else:
            assert m == c, (v, m, c)


def test_effect_size_parity():
    (m,) = mcp_calls([("chi2_effect_size", {"rates": [0.6, 0.4]})])
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    p = subprocess.run([sys.executable, "-m", "powerchi", "--test", "chi2-contingency", "--mode", "effect-size",
                        "--rates", "0.6,0.4"], capture_output=True, text=True, env=env)
    assert m == json.loads(p.stdout)
