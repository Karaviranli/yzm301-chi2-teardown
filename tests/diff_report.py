"""Diferansiyel test ve uyum raporu.

CLI'yi KARA KUTU olarak (alt süreçle, sözleşmedeki komutla) çalıştırır ve
üç kâhinle karşılaştırır:

  1. oracle/gpower_vectors.csv  -> G*Power arayüzünden elle toplanan değerler (asıl kâhin)
  2. oracle/dok_vectors.csv     -> kılavuz / yayınlardaki örnekler
  3. oracle/library_vectors.csv -> bağımsız kütüphane (500+ vektör, kesirli N)

Tolerans (yönerge e): N TAM eşleşmeli; diğer değerler G*Power'ın ekranda
gösterdiği basamak sayısına kadar eşleşmeli (kaydedilen değerin basamak sayısı
kadar yuvarlanarak karşılaştırılır).

Çalıştır:  python tests/diff_report.py      -> tests/UYUM_RAPORU.md yazar
"""

from __future__ import annotations

import csv
import json
import math
import os
import pathlib
import subprocess
import sys
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
ORACLE = ROOT / "oracle"
REPORT = ROOT / "tests" / "UYUM_RAPORU.md"


def cli(args: list[str]) -> tuple[dict, int]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    p = subprocess.run([sys.executable, "-m", "powerchi", *args], capture_output=True,
                       text=True, env=env)
    line = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "{}"
    return json.loads(line), p.returncode


def decimals(s: str) -> int:
    s = s.strip()
    return len(s.split(".")[1]) if "." in s else 0


def close_to_display(ours: float, theirs: str) -> bool:
    d = decimals(theirs)
    return round(ours, d) == round(float(theirs), d)


def fmt_args(r: dict) -> list[str]:
    a = ["--test", "chi2-contingency", "--mode", r["mode"], "--w", r["w"], "--alpha", r["alpha"],
         "--df", r["df"], "--precision", "7"]
    if r["mode"] == "a-priori":
        a += ["--power", r["power"]]
    else:
        a += ["--n", r["n"]]
    return a


def gpower_section() -> tuple[list[str], dict]:
    rows = list(csv.DictReader((ORACLE / "gpower_vectors.csv").open(encoding="utf-8")))
    filled = [r for r in rows if (r["gp_n_total"] or r["gp_power"] or r["gp_message"]).strip()]
    lines = ["## 1. G*Power arayüz vektörleri (asıl kâhin)", ""]
    stats = {"toplam": len(rows), "dolu": len(filled), "n_eslesen": 0, "n_karsilastirilan": 0,
             "tam_eslesen": 0}
    if not filled:
        lines += [f"> {len(rows)} vektörün girdileri hazır, G*Power çıktıları henüz girilmedi.",
                  "> `oracle/gpower_vectors.csv` dosyasındaki `gp_*` sütunlarını G*Power 3.1.9.7 ekranından doldurun",
                  "> ve ekran görüntüsünü `oracle/screenshots/<id>.png` olarak kaydedin. Sonra bu betiği yeniden çalıştırın.", ""]
        return lines, stats
    lines += ["| id | kategori | girdi | G*Power | bizim | N | diğer | not |", "|---|---|---|---|---|---|---|---|"]
    for r in filled:
        ours, code = cli(fmt_args(r))
        gp_err = r["gp_message"].strip()
        if "error" in ours or gp_err:
            same = ("error" in ours) == bool(gp_err) and not r["gp_n_total"].strip()
            n_ok = other_ok = same
            ours_s = ours.get("error", json.dumps(ours))[:60]
            gp_s = gp_err or r["gp_n_total"]
        else:
            if r["mode"] == "a-priori":
                n_ok = str(ours["n_total"]) == r["gp_n_total"].strip()
                pw_key = "actual_power"
            else:
                n_ok = True
                pw_key = "power"
            checks = []
            for ours_v, gp_v in ((ours[pw_key], r["gp_power"]), (ours["critical"], r["gp_critical"]),
                                 (ours["ncp"], r["gp_ncp"])):
                if gp_v.strip():
                    checks.append(close_to_display(ours_v, gp_v))
            other_ok = all(checks) if checks else True
            ours_s = f"N={ours['n_total']} güç={ours[pw_key]:.7f}"
            gp_s = f"N={r['gp_n_total']} güç={r['gp_power']}"
        if r["mode"] == "a-priori":
            stats["n_karsilastirilan"] += 1
            stats["n_eslesen"] += int(n_ok)
        stats["tam_eslesen"] += int(n_ok and other_ok)
        inp = f"w={r['w']} α={r['alpha']} " + (f"güç={r['power']}" if r["mode"] == "a-priori" else f"N={r['n']}") + f" df={r['df']}"
        lines.append(f"| {r['id']} | {r['category']} | {inp} | {gp_s} | {ours_s} | {'✅' if n_ok else '❌'} | "
                     f"{'✅' if other_ok else '❌'} | {r['notes']} |")
    if stats["n_karsilastirilan"]:
        rate = 100 * stats["n_eslesen"] / stats["n_karsilastirilan"]
        lines += ["", f"**N tam eşleşme (a priori): {stats['n_eslesen']}/{stats['n_karsilastirilan']} = {rate:.1f}%** "
                      f"(kapı: ≥ %90) · tüm alanlarda eşleşen: {stats['tam_eslesen']}/{len(filled)}", ""]
    return lines, stats


def dok_section() -> list[str]:
    lines = ["## 2. Kılavuz / yayın örnekleri [DOK]", "", "| id | girdi | beklenen N | bizim N | sonuç |", "|---|---|---|---|---|"]
    for r in csv.DictReader((ORACLE / "dok_vectors.csv").open(encoding="utf-8")):
        ours, _ = cli(["--test", "chi2-contingency", "--mode", r["mode"], "--w", r["w"], "--alpha", r["alpha"],
                       "--power", r["power"], "--df", r["df"]])
        ok = str(ours.get("n_total")) == r["n_total"]
        lines.append(f"| {r['id']} | w={r['w']} α={r['alpha']} güç={r['power']} df={r['df']} | {r['n_total']} | "
                     f"{ours.get('n_total')} | {'✅' if ok else '❌'} |")
    return lines + [""]


def library_section() -> list[str]:
    sys.path.insert(0, str(ROOT / "src"))
    from powerchi import engine  # motor doğrudan; 630 alt süreç gereksiz yavaş olur
    rows = list(csv.DictReader((ORACLE / "library_vectors.csv").open(encoding="utf-8")))
    mism, frac_close = [], 0
    for r in rows:
        e = engine.a_priori(float(r["w"]), float(r["alpha"]), float(r["power"]), int(r["df"]))
        if e.n_total != int(r["n_ceil"]):
            mism.append((r["id"], e.n_total, r["n_ceil"]))
        nf = float(r["n_fractional"])
        if nf - math.floor(nf) < 1e-3 or math.ceil(nf) - nf < 1e-3:
            frac_close += 1
    lines = ["## 3. Bağımsız kütüphane vektörleri (ölçek)", "",
             f"- Vektör sayısı: **{len(rows)}** (w × α × güç × df ızgarası)",
             f"- Motor N = ⌈kesirli N⌉ eşleşmesi: **{len(rows) - len(mism)}/{len(rows)}**",
             f"- Kesirli N'si bir tam sayıya 0,001'den yakın (yuvarlama açısından riskli) vektör: {frac_close}",
             "- Not: kütüphane kesirli N verir (ör. 87,2), G*Power ve motor yukarı yuvarlar (88). "
             "Bu fark beklenen bir bulgudur; motor 'güç ≥ hedef olan en küçük tam sayı'yı arar (SPEC §3.3).", ""]
    for m in mism[:20]:
        lines.append(f"  - ❌ {m[0]}: motor {m[1]} / kütüphane ⌈N⌉ {m[2]}")
    return lines


def main() -> None:
    g_lines, stats = gpower_section()
    out = [f"# Uyum raporu (diferansiyel test)", "",
           f"Üretildi: {datetime.now():%Y-%m-%d %H:%M} · `python tests/diff_report.py`", ""]
    out += g_lines + dok_section() + library_section()
    REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"rapor -> {REPORT}")
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
