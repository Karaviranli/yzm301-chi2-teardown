# powerchi: χ² olumsallık tablosu için güç analizi (CLI + MCP + Türkçe ajan)

**YZM301 Yazılım Gerçekleme ve Test · Teardown Sprint · Test ailesi K4: χ² testi, olumsallık tablosu (yanıt oranları)**
Öğrenci: 241478067 (Grup 7, bireysel)

## Yapılan katmanlar

| Katman | Durum | Nerede |
|---|---|---|
| Temel: CLI (`gpower-clone`) | ✅ | `src/powerchi/engine.py`, `src/powerchi/cli.py` |
| +15 MCP sunucusu | ✅ | `src/powerchi/mcp_server.py`, parite testi `tests/test_mcp_parity.py` |
| +10 AI ajanı (Türkçe, MCP üzerinden) | ✅ | `src/powerchi/agent.py`, `agent_eval/` |
| İsteğe bağlı: Sistem 1 sınıflandırıcı | ✅ (Jev yerine etiket setine kısıtlı LLM) | `agent.py` → `classify()` |

Hesap mantığı **tek motordadır** (`engine.py`). CLI, MCP ve ajan yalnızca bu motoru çağırır. Ajan hiçbir sayı üretmez.

---

## Kurulum

```bash
# Python 3.10+
python -m pip install -e ".[mcp]"          # motor + CLI + MCP
python -m pip install -e ".[mcp,dev]"      # + testler (pytest, statsmodels)
```

Sürüm: powerchi 1.0.0 · Python 3.13 · scipy 1.18 · mcp 2.3 ile test edildi.
Referans: **G*Power 3.1.9.7 (Windows)**, yalnızca resmi sayfadan: https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower

İncelenen dosya (resmi Windows paketi `GPowerWin_3.1.9.7.zip` içinden, sürüm bilgisi: *G\*Power 3.1.9.7, Franz Faul*):

| Dosya | SHA-256 |
|---|---|
| `GPowerWin_3.1.9.7.zip` | `3bb7f1f2478d74ee5ba701ae7f849373cf2b8a11f6b6216c7c6b236db7861199` |
| `GPower_3.1.9.7_143/GPowerNT.exe` | `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812` |

Not: Bu sürümde çalıştırılabilir dosyanın adı `GPowerNT.exe` (yönergedeki `GPower.exe` ile aynı program). Binary bu repoya **konmaz** (`.gitignore`).

## REA kontrolü

> Ajana sorulan: "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?"
>
> İnceleme oturumunun (2026-10-21) cevabı: **Hayır, 0 araç.** Oturumda REA araçları ve Ghidra sağlayıcısı yüklü değildi; makinede Ghidra ve JDK 21 de yoktu. Ayrıntı: AGENT_COST.md, Oturum 1.

## Teslim durumu (dürüstçe)

| Parça | Durum |
|---|---|
| G*Power kâhini | ✅ 45 vektör, her biri ekran görüntüsüyle (`oracle/`) |
| Diferansiyel test | ✅ `tests/UYUM_RAPORU.md`: a priori N **37/37 = %100** (kapı %90), tüm alanlar 45/45; 93 test geçiyor |
| SPEC (Gherkin) | ✅ kâhine göre güncellendi (§3.7, §4, §4b, §6, §8, §9) |
| HALLUCINATIONS | ✅ H-01…H-03 (yazım), H-11…H-14 (inceleme) |
| LEDGER [REA] satırları | ❌ boş: REA/Ghidra kurulu değildi, adres kanıtı toplanamadı |
| Ajan değerlendirmesi / token ölçümü | ❌ çalıştırılmadı: `ANTHROPIC_API_KEY` tanımlı değildi (kod ve 10 soruluk set hazır: `agent_eval/`) |
| Demo videosu | ✅ `docs/demo.mp4` (60 sn) |

## Demo

60 saniyelik CLI videosu: [docs/demo.mp4](docs/demo.mp4) (repoda; GitHub'da dosyaya tıklayınca oynatılır). Komutlar gerçekten çalıştırılıp çıktıları kaydedildi; görüntü `docs/make_demo.py` ile çizildi, yeniden üretmek için: `python docs/make_demo.py`. İçerik: a priori, post hoc, güç = α sınırı, kesirli df, geçersiz girdi (çıkış kodu 2), etki büyüklüğü, `pytest` (93 geçen), `diff_report` (37/37).

---

## CLI

```bash
# A priori: kaç denek?
gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.8 --df 1
{"n_total":88,"actual_power":0.8035,"critical":3.8415,"df":1,"ncp":7.92}

# Post hoc: gücüm neydi?
gpower-clone --test chi2-contingency --mode post-hoc --w 0.3 --alpha 0.05 --n 88 --df 1
{"n_total":88,"power":0.8035,"critical":3.8415,"df":1,"ncp":7.92}

# Etki büyüklüğü: yanıt oranlarından w
gpower-clone --test chi2-contingency --mode effect-size --rates 0.6,0.4
{"w":0.2,"df":1,"rows":2,"cols":2}
gpower-clone --test chi2-contingency --mode effect-size --rates 0.40,0.25 --weights 2,1
gpower-clone --test chi2-contingency --mode effect-size --table "0.3,0.2;0.2,0.3"

# Geçersiz girdi → {"error": "..."} ve çıkış kodu 2
gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.04 --df 1
```

| Parametre | Anlam |
|---|---|
| `--test` | `chi2-contingency` |
| `--mode` | `a-priori` · `post-hoc` · `effect-size` |
| `--w` | Cohen w (a priori > 1e-6; post hoc ≥ 0) |
| `--alpha` | (0, 1) |
| `--power` | [α, 1), a priori (güç = α geçerli → N = 1) |
| `--n` | toplam N, post hoc; kesirli değer en yakın tam sayıya yuvarlanır (.5 yukarı), yuvarlanmış N ∈ [1, 2 147 483 646], `n_total` yuvarlanmış değerdir |
| `--df` | (satır−1)(sütun−1); kesirli değer en yakın tam sayıya yuvarlanır (.5 yukarı), yuvarlanmış df ≥ 1, çıktıdaki `df` yuvarlanmış değerdir |
| `--precision` | çıktı ondalığı, varsayılan 4 |

Kurulum yapmadan: `python -m powerchi ...` (repo kökünde `PYTHONPATH=src`) ya da Windows'ta `gpower-clone.cmd ...`.

## MCP sunucusu

```bash
python -m powerchi.mcp_server     # stdio
```

Claude Desktop / Claude Code yapılandırması:

```json
{
  "mcpServers": {
    "powerchi": { "command": "python", "args": ["-m", "powerchi.mcp_server"] }
  }
}
```

### Araç şeması

**`chi2_contingency_power`**

| Girdi | Tip | Zorunlu | Açıklama |
|---|---|---|---|
| `mode` | string | ✓ | `a-priori` / `post-hoc` |
| `w` | number | ✓ | Cohen w |
| `alpha` | number | ✓ | I. tip hata |
| `df` | number | ✓ | serbestlik derecesi (kesirliyse en yakın tam sayıya, .5 yukarı) |
| `power` | number | a priori | hedef güç |
| `n` | number | post hoc | toplam N (kesirliyse en yakın tam sayıya, .5 yukarı) |

Çıktı: CLI ile **birebir aynı** JSON. A priori: `{n_total, actual_power, critical, df, ncp}` · Post hoc: `{n_total, power, critical, df, ncp}` · Hata: `{error}`.

**`chi2_effect_size`**

| Girdi | Tip | Açıklama |
|---|---|---|
| `rates` | number[] | grupların yanıt oranları (0..1) |
| `weights` | number[] | grup payları (varsayılan eşit) |
| `table` | number[][] | H1 hücre olasılıkları/frekansları (`rates` yerine) |

Çıktı: `{w, df, rows, cols}` ya da `{error}`.

Parite: `tests/test_mcp_parity.py` 19 vektörü (geçersizler dahil) hem CLI'ye (alt süreç) hem MCP'ye gönderir; çıktılar birebir aynıdır.

## AI ajanı

```bash
set ANTHROPIC_API_KEY=...        # Windows (PowerShell: $env:ANTHROPIC_API_KEY="...")
python -m powerchi.agent "Standart tedavide iyileşme %60, yenisinde %75 bekliyoruz. α=0,05, %80 güç için kaç hasta?"
```

1. **Sistem 1:** etiket setine kısıtlı hızlı model (`t2-indep, t-paired, anova-oneway, chi2-contingency, multireg-r2, ambiguous, unsupported`) + güven. Güven < 0,75 ya da ambiguous/unsupported ise araştırmacıya sorulur. Jev erişimi olmadığından küçük bir Claude modeli kullanıldı.
2. **Sistem 2:** parametreleri çıkarır, `chi2_effect_size` → `chi2_contingency_power` araçlarını MCP üzerinden çağırır.
3. Her çağrı `logs/agent_calls.jsonl`'e yazılır (araç girdi/çıktısı, token, süre).

Değerlendirme: `python agent_eval/run_eval.py` → `agent_eval/EVAL_RAPORU.md` (10 soru, TR + EN, kalibrasyon).
Token karşılaştırması: `python agent_eval/token_compare.py` → `agent_eval/TOKEN_KARSILASTIRMA.md`.

## Testler ve diferansiyel test

```bash
python -m pytest -q                  # 93 test: motor, CLI sözleşmesi, 630 kütüphane vektörü, MCP paritesi, ajan tesisatı
python tests/diff_report.py          # → tests/UYUM_RAPORU.md (G*Power, [DOK] ve kütüphane kâhinleri)
python oracle/gen_library_vectors.py # 630 ölçek vektörünü yeniden üretir (statsmodels kuruluysa onu da ekler)
```

Üç katmanlı kâhin:
1. `oracle/gpower_vectors.csv`: G*Power arayüzünden elle, ekran görüntüleriyle (`oracle/screenshots/`) 45 vektör: mutlu yol, sınır değerler, geçersiz girdiler, post hoc, kesirli df (E01–E05)
2. `oracle/dok_vectors.csv`: yayınlanmış örnekler
3. `oracle/library_vectors.csv`: 630 vektör; bağımsız Poisson serisi + sürekli kök (pwr tarzı kesirli N). Motor 630/630 ⌈N⌉ ile eşleşiyor.

Kütüphaneler N'yi kesirli verir (ör. 87,2), G*Power ve bu motor yukarı yuvarlar (88). Motor, "güç ≥ hedef olan en küçük tam sayı"yı tam sayılar üzerinde ikili aramayla bulur. Böylece kesirli kökün kayan nokta hatasından etkilenmez.

## Repo yapısı

```
SPEC.md  LEDGER.md  HALLUCINATIONS.md  AGENT_COST.md
prompts/        iki oturumun ilk prompt'ları
oracle/         G*Power vektörleri (CSV) + ekran görüntüleri, [DOK] vektörleri, kütüphane vektörleri
src/powerchi/   engine.py (motor) · cli.py · mcp_server.py · agent.py
tests/          birim, sözleşme, parite, ajan tesisatı, diff_report.py → UYUM_RAPORU.md
agent_eval/     10 soruluk değerlendirme, token karşılaştırması
docs/           REA adımları, ekran görüntüleri
```

## Etik

* Yalnızca G*Power 3.1.9.7 incelendi; eğitim amaçlı. `GPower.exe` ve decompile çıktısı repoda yoktur.
* Bu yazılım G*Power değildir ve öyle sunulmaz. CLI adı (`gpower-clone`) yalnızca ders sözleşmesi gereğidir.
* Ajana yalnızca kurgusal araştırma senaryoları gönderilir; gerçek hasta verisi gönderilmez.

## Atıf

G*Power yazarlarına teşekkürle:

* Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods, 39*, 175–191.
* Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses. *Behavior Research Methods, 41*, 1149–1160.
* Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.).
