"""Ajan tesisatı testi (API anahtarı gerekmez).

LLM yanıtları sahte (_post yerine senaryo), ama MCP sunucusu GERÇEK alt süreçtir.
Doğrulanan: sınıflandırma kapısı, araç çağrı zinciri, sayıların motordan gelmesi, log.
"""

import json

import pytest

pytest.importorskip("mcp")

from powerchi import agent, engine  # noqa: E402


def scripted(responses):
    it = iter(responses)

    def fake_post(payload):
        return next(it)
    return fake_post


def _cls(label, conf):
    return {"content": [{"type": "text", "text": json.dumps({"label": label, "confidence": conf, "reason": "test"})}],
            "usage": {"input_tokens": 100, "output_tokens": 10}}


def test_chi2_flow_numbers_come_from_engine(monkeypatch, tmp_path):
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(agent, "_post", scripted([
        _cls("chi2-contingency", 0.95),
        {"content": [{"type": "tool_use", "id": "t1", "name": "chi2_effect_size", "input": {"rates": [0.75, 0.6]}}],
         "usage": {"input_tokens": 500, "output_tokens": 30}},
        {"content": [{"type": "tool_use", "id": "t2", "name": "chi2_contingency_power",
                      "input": {"mode": "a-priori", "w": 0.1601, "alpha": 0.05, "power": 0.8, "df": 1}}],
         "usage": {"input_tokens": 600, "output_tokens": 30}},
        {"content": [{"type": "text", "text": "Toplam 307 hasta gerekir."}],
         "usage": {"input_tokens": 700, "output_tokens": 20}},
    ]))
    r = agent.ask("Standartta %60, yenide %75 yanıt; α=0,05, %80 güç; kaç hasta?")
    assert r.label == "chi2-contingency" and not r.asked_researcher
    assert [c["tool"] for c in r.tool_calls] == ["chi2_effect_size", "chi2_contingency_power"]
    assert r.tool_calls[0]["output"]["w"] == engine.w_from_rates([0.75, 0.6]).to_dict()["w"]
    assert r.tool_calls[1]["output"] == engine.a_priori(0.1601, 0.05, 0.8, 1).to_dict()
    assert r.usage.calls == 4 and r.usage.input_tokens == 1900
    log = (tmp_path / "agent_calls.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(log) == 1 and json.loads(log[0])["tool_calls"][1]["output"]["n_total"] == 307


@pytest.mark.parametrize("label,conf", [("ambiguous", 0.9), ("chi2-contingency", 0.6), ("unsupported", 0.99),
                                        ("uydurma-etiket", 0.99)])
def test_gate_asks_researcher(monkeypatch, tmp_path, label, conf):
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(agent, "_post", scripted([_cls(label, conf)]))
    r = agent.ask("kaç kişi lazım?")
    assert r.asked_researcher and not r.tool_calls


def test_out_of_scope_family_no_calculation(monkeypatch, tmp_path):
    monkeypatch.setattr(agent, "LOG_DIR", tmp_path)
    monkeypatch.setattr(agent, "_post", scripted([_cls("t2-indep", 0.97)]))
    r = agent.ask("d=0,5 ile iki grup ortalaması")
    assert not r.asked_researcher and not r.tool_calls
    assert "t2-indep" in r.answer
