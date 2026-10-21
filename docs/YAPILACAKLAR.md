# Teslimden önce senin makinende yapılacaklar (sırasıyla)

Kod, testler, MCP, ajan ve belgeler hazır. Aşağıdakiler ise G*Power'ın ve REA'nın **senin bilgisayarında gerçekten çalıştırılmasını** gerektiriyor. Hocanın puanladığı kanıtlar bunlar, uydurulamaz. Toplam süre yaklaşık 2–3 saat.

## 0. Kurulum (≈20 dk)

```powershell
node -v                                   # 24.22 kurulu: uygun
npx rea-agents setup                      # yalnızca resmi paket: rea-agents (github.com/morluto/rea)
npm install --global rea-agents
rea --help
```
* Ghidra (ghidra-sre.org) + JDK 21
* G*Power 3.1.9.7: **yalnızca** psychologie.hhu.de resmi sayfasından
* Repo klasöründe: `python -m pip install -e ".[mcp,dev]"` sonra `python -m pytest -q` (69 test geçmeli)

## 1. Hash ve REA kontrolü (≈5 dk) → README

```powershell
Get-FileHash "C:\Program Files\G*Power\GPower.exe" -Algorithm SHA256
```
* Hash'i README'deki `<buraya ...>` yerine yaz.
* Ajanına (Claude Code vb.) sor: "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi? Kaç araç aktif?" Ekran görüntüsünü `docs/rea_kontrol.png` olarak kaydet. Cevabı AGENT_COST.md'deki ilgili satıra yaz.

## 2. G*Power vektörleri (≈60 dk) → `oracle/gpower_vectors.csv` (25 puanın kaynağı)

G*Power'da: **Test family:** χ² tests → **Statistical test:** Goodness-of-fit tests: Contingency tables → **Type of power analysis:** A priori (ya da Post hoc).

`oracle/gpower_vectors.csv` dosyasındaki 40 satırın her biri için:
1. `w`, `alpha`, `power` (ya da `n`), `df` değerlerini girip **Calculate**'e bas.
2. Ekrandaki değerleri **gösterildiği gibi, tüm basamaklarıyla** yaz:
   `gp_n_total` (Total sample size), `gp_power` (Actual power / Power), `gp_critical` (Critical χ²), `gp_ncp` (Noncentrality parameter λ).
3. G*Power hata ya da uyarı veriyor veya alanı kabul etmiyorsa sayıları boş bırak, `gp_message` sütununa ne olduğunu yaz (ör. "power must be > alpha" / "alan kırmızı oldu, hesaplamadı" / "df'yi 2'ye yuvarladı").
4. Pencerenin ekran görüntüsünü `oracle/screenshots/<id>.png` olarak kaydet (Win+Shift+S).

Sonra:
```powershell
python tests/diff_report.py      # tests/UYUM_RAPORU.md üretir, N eşleşme oranını yazar (kapı: ≥ %90)
```
**Uyuşmazlık çıkarsa** bu bir bulgudur: hangi kural (SPEC §9) farklıysa LEDGER'a yaz, SPEC'i düzelt, motoru yeni oturumda düzelt (prompts/oturum2_yazim.md). Özellikle B03–B05 (N alt sınırı) ve I01–I09 (geçersiz girdi) satırlarına dikkat et. Motorun alt sınırı tek satırdır: `engine.N_MIN`.

## 3. REA inceleme oturumu (≈45 dk) → LEDGER.md §B (20 puan)

Yeni bir ajan oturumu aç, `prompts/oturum1_inceleme.md` içindeki prompt'u ver. Ajanın bulduğu her şey için:
* LEDGER.md §B tablosundaki `*doldurulacak*` hücrelerine **fonksiyon adresi + dize referansı** yaz.
* Ajan bir şeyi söyleyip adres gösteremiyorsa satır [AJAN] kalır.
* Ajan yanlış bir şey iddia edip vektör/test bunu yakalarsa HALLUCINATIONS.md'ye ekle (en az 2 tane zaten var; REA'dan 1–2 tane daha eklemek iyi olur).
* Oturumun token/maliyet bilgisini AGENT_COST.md'ye yaz.
* Decompile kodunu hiçbir dosyaya yapıştırma.

## 4. Ajan değerlendirmesi ve token ölçümü (≈30 dk) → bonus +10

```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
python agent_eval/run_eval.py          # 10 soru TR + EN → agent_eval/EVAL_RAPORU.md, logs/agent_calls.jsonl
```
GUI yolu için: Q01–Q07 sorularını G*Power'da elle çöz, her adımın ekran görüntüsünü `agent_eval/gui_screens/Q01_1.png`, `Q01_2.png`, ... olarak kaydet. Süreyi ve G*Power'ın verdiği N'yi `agent_eval/gui_runs.csv`'ye yaz. Sonra:
```powershell
python agent_eval/token_compare.py     # agent_eval/TOKEN_KARSILASTIRMA.md
```
`logs/agent_calls.jsonl`'i de repoya ekle (`.gitignore`'dan `logs/` satırını sil).

## 5. Demo (≈10 dk)

60 saniyelik ekran kaydı: üç CLI çağrısı (a priori, post hoc, geçersiz girdi) + `python -m pytest -q`. YouTube (liste dışı) ya da Drive linkini README'ye koy.

## 6. GitHub'a gönder

```powershell
git remote add origin https://github.com/<kullanıcı-adın>/yzm301-chi2-teardown.git
git add -A
git commit -m "G*Power vektörleri, REA kanıtları, değerlendirme"
git push -u origin main
```
Linki ödev formuna yapıştır.
