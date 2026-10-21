"""10 soruluk ajan değerlendirmesi (Türkçe + İngilizce) ve kalibrasyon.

Çalıştır (ANTHROPIC_API_KEY gerekli):
    python agent_eval/run_eval.py              # her iki dil
    python agent_eval/run_eval.py --lang tr
    python agent_eval/run_eval.py --check      # API'siz: beklenen değerleri motorla yeniden doğrular

Çıktılar:
    agent_eval/results_<lang>.jsonl   ham sonuçlar (araç çağrıları dahil)
    agent_eval/EVAL_RAPORU.md         doğru seçim oranı, parametre/N doğruluğu, kalibrasyon, TR↔EN
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
HERE = ROOT / "agent_eval"

from powerchi import engine  # noqa: E402

QUESTIONS = [json.loads(l) for l in (HERE / "questions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def recompute(q: dict) -> dict | None:
    p = q["expected_params"]
    if q["expected_label"] != "chi2-contingency":
        return None
    w = engine.w_from_rates(p["rates"], p.get("weights")).w if "rates" in p else p["w"]
    if p["mode"] == "a-priori":
        return engine.a_priori(w, p["alpha"], p["power"], p["df"]).to_dict()
    return engine.post_hoc(w, p["alpha"], p["n"], p["df"]).to_dict()


def check() -> int:
    bad = 0
    for q in QUESTIONS:
        r = recompute(q)
        if r is not None and r != q["expected"]:
            bad += 1
            print("UYUŞMAZ", q["id"], r, q["expected"])
    print(f"{len(QUESTIONS)} soru, {bad} uyuşmazlık")
    return 1 if bad else 0


def score(q: dict, res: dict) -> dict:
    exp_label = q["expected_label"]
    s = {"id": q["id"], "label_ok": res["label"] == exp_label, "params_ok": None, "n_ok": None}
    if exp_label == "ambiguous":
        s["label_ok"] = res["asked_researcher"]  # belirsizlikte araştırmacıya sormak doğru davranış
        s["n_ok"] = not res["tool_calls"]
        return s
    if exp_label != "chi2-contingency":
        s["n_ok"] = not res["tool_calls"]  # kapsam dışı: hesap yapılmamalı
        return s
    power_calls = [c for c in res["tool_calls"] if c["tool"] == "chi2_contingency_power"]
    if not power_calls:
        s["params_ok"] = s["n_ok"] = False
        return s
    last = power_calls[-1]
    inp, out = last["input"], last["output"]
    p = q["expected_params"]
    s["params_ok"] = (inp.get("mode") == p["mode"] and int(inp.get("df", -1)) == p["df"]
                      and abs(float(inp.get("alpha", -1)) - p["alpha"]) < 1e-9
                      and abs(float(inp.get("w", -1)) - (p.get("w") or 0)) < 5e-3
                      and (p["mode"] != "a-priori" or abs(float(inp.get("power", -1)) - p["power"]) < 1e-9)
                      and (p["mode"] != "post-hoc" or int(inp.get("n", -1)) == p["n"]))
    if p["mode"] == "a-priori":
        s["n_ok"] = out.get("n_total") == q["expected"]["n_total"]
    else:
        s["n_ok"] = out.get("power") == q["expected"]["power"]
    return s


def calibration(rows: list[dict]) -> list[str]:
    buckets = [(0.0, 0.5), (0.5, 0.75), (0.75, 0.9), (0.9, 1.01)]
    out = ["| güven aralığı | soru | doğru etiket | doğruluk |", "|---|---|---|---|"]
    for lo, hi in buckets:
        b = [r for r in rows if lo <= r["confidence"] < hi]
        if b:
            ok = sum(r["score"]["label_ok"] for r in b)
            out.append(f"| {lo:.2f}–{min(hi, 1):.2f} | {len(b)} | {ok} | {100 * ok / len(b):.0f}% |")
    return out


def run(langs: list[str]) -> None:
    from powerchi import agent
    report = ["# Ajan değerlendirme raporu", "",
              f"Sınıflandırıcı (Sistem 1): `{agent.CLASSIFIER_MODEL}` (etiket setine kısıtlı LLM; Jev erişimi yok) · "
              f"Ajan (Sistem 2): `{agent.AGENT_MODEL}` · güven eşiği {agent.CONF_THRESHOLD}", ""]
    summary = {}
    for lang in langs:
        rows = []
        for q in QUESTIONS:
            text = q["question_tr"] if lang == "tr" else q["question_en"]
            res = agent.ask(text).to_dict()
            res["score"] = score(q, res)
            res["id"] = q["id"]
            rows.append(res)
            print(lang, q["id"], res["label"], res["score"])
        with (HERE / f"results_{lang}.jsonl").open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        lab = sum(r["score"]["label_ok"] for r in rows)
        nq = [r for r in rows if r["score"]["n_ok"] is not None]
        nok = sum(bool(r["score"]["n_ok"]) for r in nq)
        tin = sum(r["usage"]["input_tokens"] for r in rows)
        tout = sum(r["usage"]["output_tokens"] for r in rows)
        secs = sum(r["seconds"] for r in rows)
        summary[lang] = (lab, nok, len(nq), tin, tout, secs)
        report += [f"## Dil: {lang.upper()}", "",
                   f"- Doğru test ailesi seçimi: **{lab}/{len(rows)}**",
                   f"- Doğru N/güç (ya da doğru biçimde hesap yapmama): **{nok}/{len(nq)}**",
                   f"- Toplam token: giriş {tin}, çıkış {tout} · toplam süre {secs:.1f} sn", "",
                   "| id | etiket | güven | araştırmacıya soruldu | etiket ✓ | param ✓ | N ✓ | araç çağrısı |",
                   "|---|---|---|---|---|---|---|---|"]
        for r in rows:
            sc = r["score"]
            f = lambda v: "—" if v is None else ("✅" if v else "❌")
            report.append(f"| {r['id']} | {r['label']} | {r['confidence']:.2f} | {'evet' if r['asked_researcher'] else 'hayır'} | "
                          f"{f(sc['label_ok'])} | {f(sc['params_ok'])} | {f(sc['n_ok'])} | {len(r['tool_calls'])} |")
        report += ["", "### Kalibrasyon", ""] + calibration(rows) + [""]
    if len(summary) == 2:
        report += ["## Türkçe ↔ İngilizce", "", "| dil | doğru etiket | doğru N | giriş token | çıkış token | süre (sn) |",
                   "|---|---|---|---|---|---|"]
        for lang, (lab, nok, nn, tin, tout, secs) in summary.items():
            report.append(f"| {lang} | {lab}/10 | {nok}/{nn} | {tin} | {tout} | {secs:.1f} |")
    (HERE / "EVAL_RAPORU.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("rapor ->", HERE / "EVAL_RAPORU.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["tr", "en", "both"], default="both")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        sys.exit(check())
    run(["tr", "en"] if a.lang == "both" else [a.lang])
