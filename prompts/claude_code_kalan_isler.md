# Claude Code: kalan işler için prompt'lar

Ödev kuralı (temiz oda) iki AYRI ajan oturumu istiyor. Bu yüzden iki prompt var:

* **Prompt A** (inceleme oturumu): kâhin değerleri, REA bulguları ve belgeler. Kod yazmaz.
* **Prompt B** (yazım oturumu): yalnızca Prompt A, SPEC.md'de bir değişiklik gerektirdiyse kullanılır. Yeni bir oturumda açılır.

Başlamadan önce PowerShell'de:

```powershell
cd C:\Users\deniz\Downloads\yzm301-chi2-teardown
git pull
npx rea-agents setup        # Claude Code'u seç, değişiklikleri onayla, Claude Code'u yeniden başlat
python -m pip install -e ".[mcp,dev]"
claude
```

---

## Prompt A: İnceleme oturumu

```
Bu klasör YZM301 "Teardown Sprint" ödevimin reposu (test ailesi K4: χ² testi, olumsallık tablosu).
Hedef program: C:\Users\deniz\Downloads\GPowerWin_3.1.9.7\GPower_3.1.9.7_143\GPowerNT.exe
(G*Power 3.1.9.7, resmi paket; SHA-256 README'de). Eğitim amaçlı inceleme, yazarlar Faul, Erdfelder,
Lang, Buchner. Önce README.md, SPEC.md, LEDGER.md, HALLUCINATIONS.md, AGENT_COST.md,
docs/YAPILACAKLAR.md ve prompts/oturum1_inceleme.md dosyalarını oku.

DEĞİŞMEZ KURALLAR
- Bu oturum İNCELEME oturumudur: src/ altındaki koda DOKUNMA. Yalnızca SPEC.md, LEDGER.md,
  HALLUCINATIONS.md, AGENT_COST.md, README.md, oracle/ ve tests/UYUM_RAPORU.md değişebilir.
- oracle/gpower_vectors.csv içindeki gp_* sütunlarına YALNIZCA G*Power ekranında gerçekten
  görülen değerler yazılır. Motordan, kütüphaneden ya da tahminle ASLA doldurma.
- LEDGER'a [REA] etiketi yalnızca fonksiyon adresi veya dize referansı gösterebildiğin iddiaya
  konur. Gösteremiyorsan [AJAN] yaz.
- Decompile edilmiş kodu hiçbir dosyaya yazma; LEDGER'da yalnızca kısa alıntı + adres.
- GPowerNT.exe ve VC_redist hiçbir zaman repoya eklenmez.

ADIMLAR
1. REA kontrolü: "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi? Kaç araç
   aktif?" sorusunu cevapla. Cevabı AGENT_COST.md'deki Oturum 1 tablosuna yaz. Bana bu cevabın
   ekran görüntüsünü docs/rea_kontrol.png olarak kaydetmemi hatırlat.

2. Kâhin değerleri: oracle/gpower_vectors.csv'de gp_* sütunları boş olan satırları listele.
   Öncelik: G10, B01–B11, I01–I09 (en az bu 21'i), sonra G11, G12, P01–P08.
   Bilgisayar kontrolü (computer use) aracın varsa G*Power'da kendin gir: χ² tests →
   Goodness-of-fit tests: Contingency tables; a priori satırlar için "A priori", P satırları için
   "Post hoc" seç. Her alanı değiştirmeden önce Ctrl+A ile seç. Calculate'ten sonra pencerenin
   görüntüsünü oracle/screenshots/<id>.jpg olarak kaydet.
   Bilgisayar kontrolün yoksa bana satırları SIRAYLA tek tek ver, ben G*Power'a girip sonucu
   (Total sample size, Actual power, Critical χ², λ ya da hata mesajı) yazayım. Sen CSV'ye işle.
   Hata/uyarı veren satırlarda sayıları boş bırakıp mesajı gp_message sütununa aynen yaz.
   Sonra: python tests/diff_report.py

3. REA incelemesi: prompts/oturum1_inceleme.md içindeki adımları GPowerNT.exe üzerinde uygula.
   Özellikle LEDGER §B'deki L-05…L-13 hipotezlerini sına. Her biri için adres/dize referansı,
   güven ve kalan bilinmeyeni LEDGER §B tablosuna yaz. Adım 2'deki kâhin sonuçlarıyla
   karşılaştır: binary'deki kural ile ekrandaki davranış tutarlı mı?

4. Uyuşmazlıklar: diff_report'ta ❌ olan her satır için nedenini bul (hangi kural farklı?).
   - SPEC.md §3, §6 ve §9'u yalnızca kanıta dayanarak güncelle (kural + [REA]/kâhin kaynağı).
   - Kendi yanlış çıkardığın ya da daha önce [AJAN] olup çürüyen her iddiayı HALLUCINATIONS.md'nin
     "İnceleme oturumu" tablosuna ekle (iddia, gerçek, nasıl fark edildi, yakalayan vektör).
   - Motoru DÜZELTME. Motorun değişmesi gerekiyorsa en sonda bana "Prompt B gerekli" de ve
     SPEC'te neyin değiştiğini özetle.

5. Ajan değerlendirmesi: ANTHROPIC_API_KEY tanımlıysa
   python agent_eval/run_eval.py  ve  python agent_eval/token_compare.py  çalıştır
   (token_compare için agent_eval/gui_screens/ altında Q01_1.png… olmalı; yoksa bana hangi
   ekranları kaydetmem gerektiğini söyle). Anahtar yoksa bu adımı atla ve README'de belirt.
   logs/agent_calls.jsonl'i repoya almak için .gitignore'daki "logs/" satırını kaldır.

6. Belgeler: AGENT_COST.md'ye bu oturumun ajanını, yaklaşık token/maliyetini, iterasyon sayısını
   ve "neyi farklı yapardım"ı yaz. README'deki uyum oranını güncelle.
   python -m pytest -q  çalıştır (src/'ye dokunmadığın için hepsi geçmeli).

7. git add -A, anlamlı bir commit mesajı, git push. Sonunda bana özet ver: N eşleşme oranı
   (kapı ≥ %90), doldurulan [REA] satırları, yeni halüsinasyon kayıtları, Prompt B gerekip
   gerekmediği ve benim yapmam gereken kalanlar (rea_kontrol.png, demo videosu).
```

---

## Prompt B: Yazım oturumu (yalnızca gerekirse, YENİ oturumda)

`/clear` ile ya da yeni bir terminalde yeni bir Claude Code oturumu aç. Bu oturuma Ghidra/REA çıktısı ve LEDGER verme.

```
Bu repoda src/powerchi/engine.py, SPEC.md'deki davranış spesifikasyonunun temiz oda
uygulamasıdır. SPEC.md yakın zamanda güncellendi. YALNIZCA SPEC.md'yi oku (LEDGER.md'yi,
oracle/screenshots'ı ve Ghidra/REA çıktısını OKUMA).

1. SPEC.md ile src/powerchi/engine.py ve cli.py arasındaki farkları listele.
2. Motoru SPEC'e uydur. Hesap mantığı yalnızca engine.py'de kalsın; cli.py ve mcp_server.py
   ince katman olarak kalsın.
3. SPEC §8'deki değişen her Gherkin senaryosu için tests/test_engine.py ya da
   tests/test_cli_contract.py'ye test ekle veya düzelt.
4. python -m pytest -q  ve  python tests/diff_report.py  çalıştır. Kâhin N eşleşmesi ≥ %90 olmalı.
5. AGENT_COST.md'ye "Oturum 2b: düzeltme turu" satırı ekle.
6. git add -A, commit, git push. Bana değişiklik özetini ve yeni uyum oranını ver.
```

---

## Sende kalan (ajanın yapamayacağı)

* `docs/rea_kontrol.png`: REA kontrol cevabının ekran görüntüsü
* 60 saniyelik demo videosu (Win+Alt+R ile kaydet): README'deki `<video linki>` yerine linkini koy
