"""60 saniyelik CLI demo videosunu üretir: docs/demo.mp4

Komutlar GERÇEKTEN çalıştırılır; videodaki her çıktı o anki çalıştırmanın çıktısıdır.
Yalnızca görüntü (terminal görünümü, yazma animasyonu) betikle çizilir.

Gerekenler: Pillow, imageio-ffmpeg
Çalıştır:   python docs/make_demo.py
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
from datetime import date

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "demo.mp4"
W, H, FPS, TOTAL_S = 1280, 720, 10, 60
FONT = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 20)
FONT_B = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 26)
BG, FG, DIM, PROMPT, OK, ERR = (18, 18, 24), (230, 230, 230), (140, 140, 150), (110, 200, 255), (120, 220, 140), (255, 120, 120)
LINE_H, MARGIN, MAX_LINES = 26, 24, 25

CMDS: list[tuple[str, list[str], str | None]] = [
    ("# A priori: kaç denek? (G*Power: N=88)",
     ["gpower-clone", "--test", "chi2-contingency", "--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8", "--df", "1"], None),
    ("# 2x6 tablo, %95 güç (G*Power: N=220)",
     ["gpower-clone", "--test", "chi2-contingency", "--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.95", "--df", "5"], None),
    ("# Post hoc: N=88 ile güç",
     ["gpower-clone", "--test", "chi2-contingency", "--mode", "post-hoc", "--w", "0.3", "--alpha", "0.05", "--n", "88", "--df", "1"], None),
    ("# Sınır: güç = α (G*Power: N=1)",
     ["gpower-clone", "--test", "chi2-contingency", "--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.05", "--df", "1"], None),
    ("# Kesirli df=1.5 -> 2 (G*Power: N=108)",
     ["gpower-clone", "--test", "chi2-contingency", "--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8", "--df", "1.5"], None),
    ("# Geçersiz girdi: güç < α -> hata, çıkış kodu != 0",
     ["gpower-clone", "--test", "chi2-contingency", "--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.04", "--df", "1"], "exit"),
    ("# Etki büyüklüğü: %60 vs %40 yanıt oranı",
     ["gpower-clone", "--test", "chi2-contingency", "--mode", "effect-size", "--rates", "0.6,0.4"], None),
    ("# Test paketi",
     [sys.executable, "-m", "pytest", "-q"], "tail2"),
    ("# Diferansiyel test: G*Power kâhinine karşı",
     [sys.executable, "tests/diff_report.py"], "tail1"),
]


def run(argv: list[str], mode: str | None) -> list[tuple[str, tuple]]:
    env = dict(os.environ, PYTHONUTF8="1")
    p = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=env)
    lines = [l for l in p.stdout.strip().splitlines() if l.strip()]
    if mode == "tail2":
        lines = lines[-1:]
    elif mode == "tail1":
        lines = lines[-1:]
    color = ERR if p.returncode else FG
    out = [(l, color) for l in lines]
    if mode == "exit":
        out.append((f"çıkış kodu: {p.returncode}", DIM))
    if mode in ("tail2", "tail1"):
        out = [(l, OK) for l in lines]
    return out


def shown(argv: list[str]) -> str:
    a = ["python" if x == sys.executable else x for x in argv]
    return " ".join(a)


def wrap(text: str, width: int = 98) -> list[str]:
    return [text[i:i + width] for i in range(0, len(text), width)] or [""]


def main() -> None:
    print("komutlar çalıştırılıyor...")
    results = [(c, shown(a), run(a, m)) for c, a, m in CMDS]
    for c, s, o in results:
        print(s, "->", [t for t, _ in o])

    # zaman çizelgesi: başlık 4 sn, kalan süre komutlara eşit bölünür
    title_frames = 4 * FPS
    per = (TOTAL_S * FPS - title_frames) // len(results)
    frames_total = title_frames + per * len(results)

    ff = imageio_ffmpeg.write_frames(str(OUT), (W, H), fps=FPS, codec="libx264", quality=7,
                                     macro_block_size=16, output_params=["-pix_fmt", "yuv420p"])
    ff.send(None)

    # başlık
    for _ in range(title_frames):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        d.text((MARGIN * 3, 220), "powerchi · χ² olumsallık tablosu güç analizi", font=FONT_B, fill=FG)
        d.text((MARGIN * 3, 270), "YZM301 Teardown Sprint · K4 · CLI demo", font=FONT, fill=DIM)
        d.text((MARGIN * 3, 320), "Gerçek komutlar ve gerçek çıktılar; görüntü docs/make_demo.py ile çizildi.", font=FONT, fill=DIM)
        d.text((MARGIN * 3, 350), f"{date.today():%Y-%m-%d} · G*Power 3.1.9.7 ile karşılaştırmalı", font=FONT, fill=DIM)
        ff.send(img.tobytes())

    history: list[tuple[str, tuple]] = []
    for comment, cmd, out in results:
        typed_full = f"> {cmd}"
        type_frames = min(per // 2, max(6, len(typed_full) // 8))
        for f in range(per):
            img = Image.new("RGB", (W, H), BG)
            d = ImageDraw.Draw(img)
            lines = list(history) + [(comment, DIM)]
            k = min(len(typed_full), int(len(typed_full) * (f + 1) / type_frames))
            for w in wrap(typed_full[:k] + ("_" if f < type_frames else "")):
                lines.append((w, PROMPT))
            if f >= type_frames + 2:
                for t, col in out:
                    lines += [(w, col) for w in wrap(t)]
            for i, (t, col) in enumerate(lines[-MAX_LINES:]):
                d.text((MARGIN, MARGIN + i * LINE_H), t, font=FONT, fill=col)
            ff.send(img.tobytes())
        history += [(comment, DIM)] + [(w, PROMPT) for w in wrap(typed_full)]
        for t, col in out:
            history += [(w, col) for w in wrap(t)]
        history.append(("", FG))
    ff.close()
    print(f"-> {OUT} ({frames_total / FPS:.0f} sn, {OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
