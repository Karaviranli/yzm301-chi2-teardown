"""MCP yolu ile GUI (ekran görüntüsü) yolunun ölçülmüş token karşılaştırması.

MCP yolu : run_eval.py'nin kaydettiği gerçek API kullanımı (results_tr.jsonl).
GUI yolu : Her soru için G*Power'ı elle çözerken alınan ekran görüntüleri
           agent_eval/gui_screens/<Qid>_<adım>.png olarak kaydedilir
           (ör. Q01_1.png = test seçimi, Q01_2.png = girdiler, Q01_3.png = sonuç).
           Bu betik her sorunun ekran görüntüsü dizisini + soruyu Anthropic
           count_tokens uç noktasına gönderip GERÇEK giriş token sayısını ölçer
           (bir ajanın o ekranları görmesi için ödeyeceği bedel).
           Süre ve G*Power'ın verdiği N, agent_eval/gui_runs.csv'ye elle girilir.

Çalıştır (ANTHROPIC_API_KEY gerekli):
    python agent_eval/token_compare.py   -> agent_eval/TOKEN_KARSILASTIRMA.md
"""

from __future__ import annotations

import base64
import csv
import json
import os
import pathlib
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
MODEL = os.environ.get("POWERCHI_AGENT_MODEL", "claude-sonnet-5-5")


def count_tokens(content: list) -> int:
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages/count_tokens",
        data=json.dumps({"model": MODEL, "messages": [{"role": "user", "content": content}]}).encode(),
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
                 "content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["input_tokens"]


def gui_tokens(qid: str, question: str) -> tuple[int, int]:
    shots = sorted((HERE / "gui_screens").glob(f"{qid}_*.png"))
    if not shots:
        return 0, 0
    total = 0
    history: list = [{"type": "text", "text": question}]
    # Ajan her adımda o ana kadarki tüm ekranları bağlamında taşır: birikimli maliyet
    for s in shots:
        history.append({"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                     "data": base64.b64encode(s.read_bytes()).decode()}})
        total += count_tokens(history)
    return total, len(shots)


def main() -> None:
    qs = {json.loads(l)["id"]: json.loads(l) for l in (HERE / "questions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    mcp_rows = {}
    rp = HERE / "results_tr.jsonl"
    if rp.exists():
        for l in rp.read_text(encoding="utf-8").splitlines():
            r = json.loads(l)
            mcp_rows[r["id"]] = r
    gui_meta = {}
    gp = HERE / "gui_runs.csv"
    if gp.exists():
        for r in csv.DictReader(gp.open(encoding="utf-8")):
            gui_meta[r["id"]] = r
    lines = ["# Token karşılaştırması: MCP yolu vs GUI (ekran görüntüsü) yolu", "",
             f"Model: `{MODEL}` · GUI token'ı count_tokens ile ölçüldü (birikimli bağlam).", "",
             "| id | MCP giriş+çıkış token | MCP süre (sn) | MCP doğru | GUI ekran sayısı | GUI giriş token | GUI süre (sn) | GUI doğru | oran (GUI/MCP) |",
             "|---|---|---|---|---|---|---|---|---|"]
    tot_m = tot_g = 0
    for qid, q in qs.items():
        m = mcp_rows.get(qid)
        mt = (m["usage"]["input_tokens"] + m["usage"]["output_tokens"]) if m else 0
        gt, ns = gui_tokens(qid, q["question_tr"])
        g = gui_meta.get(qid, {})
        tot_m += mt
        tot_g += gt
        ratio = f"{gt / mt:.1f}×" if mt and gt else "—"
        lines.append(f"| {qid} | {mt or '—'} | {m['seconds'] if m else '—'} | "
                     f"{'✅' if m and m['score']['n_ok'] else ('❌' if m else '—')} | {ns or '—'} | {gt or '—'} | "
                     f"{g.get('seconds', '—')} | {g.get('correct', '—')} | {ratio} |")
    lines += ["", f"**Toplam:** MCP {tot_m} token · GUI {tot_g} token" +
              (f" · GUI/MCP = {tot_g / tot_m:.1f}×" if tot_m and tot_g else "")]
    (HERE / "TOKEN_KARSILASTIRMA.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("rapor ->", HERE / "TOKEN_KARSILASTIRMA.md")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY tanımlı değil")
    main()
