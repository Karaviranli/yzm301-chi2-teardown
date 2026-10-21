# Ajan maliyet ve süreç günlüğü

## Oturum 2: Yazım (motor, CLI, MCP, ajan, testler, belgeler)

| Alan | Değer |
|---|---|
| Ajan | Claude (model `claude-opus-5-5`), Claude uygulamasındaki ajan oturumu |
| Yaklaşık token | ≈ 250 bin (oturumun bağlam sayacından; araç çıktıları dahil) |
| Yaklaşık maliyet | Abonelik kapsamında; API fiyatıyla kabaca birkaç USD mertebesi |
| İterasyon | Motor 1 tur; CLI 1 tur; test paketi 4 çalıştırma (60 geçen → MCP paritesi 3 geçen → 68 geçen + 1 düşen (H-02) → 69 geçen); MCP 1 tur (H-01 düzeltmesi); ajan 2 tur (H-02 düzeltmesi) |
| Görülen kaynaklar | Ödev yönergesi, ders slaytları, belgelenmiş bir G*Power vektörü (L-01). Ghidra/decompile çıktısı GÖRÜLMEDİ. |
| Kâhin | Bağımsız seri uygulaması ile 630 vektör, 630/630 N eşleşmesi |

**Neyi farklı yapardım:**
1. Önce G*Power ekranından 40 vektörü toplar, motoru ancak sonra yazardım. "Önce davranışı test olarak yakala." Bu oturumda G*Power'a erişim yoktu, sıra tersine döndü.
2. MCP SDK sürümünü ilk adımda sabitler, ajanın bellekteki API'sine güvenmezdim (H-01).
3. Alt süreç başlatan her kod için ilk gün uçtan uca test yazardım (H-02).

## Oturum 1: İnceleme (REA + Ghidra)

| Alan | Değer |
|---|---|
| Ajan | Claude (model `claude-opus-5-5`), Claude masaüstü uygulamasındaki Claude Code oturumu, bilgisayar kontrolü (computer use) ile |
| REA araç sayısı | **0.** "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?" sorusunun cevabı: hayır; oturumda REA araçları ve Ghidra sağlayıcısı yüklü değildi, makinede Ghidra ve JDK 21 de yoktu (yalnızca Java 8). |
| Yapılan | G*Power 3.1.9.7 arayüzüne 36 vektör girildi (31 boş vektör + kesirli df kuralını ayırmak için 5 ek), her biri ekran görüntüsüyle; diff_report çalıştırıldı; SPEC §3, §4, §6, §8, §9 kâhine göre güncellendi; HALLUCINATIONS H-11…H-14 |
| Yaklaşık token | ≈ 300–400 bin (oturumun bağlam sayacından). Büyük kısmı ekran görüntüleri: ~85 ekran görüntüsü/yakınlaştırma |
| Yaklaşık maliyet | Abonelik kapsamında; API fiyatıyla kabaca 5–10 USD mertebesi (tahmin) |
| İterasyon | G*Power girişi 20 tur (tur başına 1–4 vektör); 1 tekrar ölçüm (I01, ekranda eski sonuç kalmış olabilir şüphesi); 1 not düzeltmesi (H-14) |
| Süre | G*Power girişi ≈ 10 dakika (36 vektör) |

**Neyi farklı yapardım:**
1. REA, Ghidra ve JDK 21 kurulumunu oturumdan ÖNCE yapardım. Bu oturumda REA yoktu; LEDGER §B'deki [REA] satırları bu yüzden boş kaldı.
2. Ekran görüntüsüyle GUI kullanmanın maliyetini burada doğrudan gördüm: her vektör ≈ 1 ekran görüntüsü + 1 yakınlaştırma. Aynı 36 vektör CLI'de birkaç yüz token tutar. Bu, sprintin "her arayüz bir maliyet transferidir" tezinin ölçülmüş örneği.
3. Ajanın yazdığı her sayısal notu ekrandaki ikinci bir değerle çapraz kontrol ettirirdim (H-14).

## Ajan katmanı (çalışma zamanı)

`agent_eval/EVAL_RAPORU.md` ve `agent_eval/TOKEN_KARSILASTIRMA.md` dosyalarında ölçülür (`python agent_eval/run_eval.py`, `python agent_eval/token_compare.py`).
