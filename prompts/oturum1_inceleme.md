# Oturum 1: İnceleme (REA + Ghidra) · ilk prompt

> Bu oturum yalnızca SPEC.md ve LEDGER.md üretir/günceller. Kod yazmaz. Decompile çıktısı repoya konmaz; ledger'a yalnızca kısa alıntı ve adres girer.

```
Rolün: tersine mühendislik inceleyicisi. Hedef, yerel diskteki G*Power 3.1.9.7 (Windows)
GPower.exe. Eğitim amaçlı inceleme; G*Power'ın yazarları Faul, Erdfelder, Lang, Buchner.
Yalnızca bu dosyayı incele.

Kapsam: χ² tests → "Goodness-of-fit tests: Contingency tables", a priori ve post hoc.

1. Önce REA araçlarının ve Ghidra sağlayıcısının bu oturumda kullanılabilir olduğunu doğrula,
   kaç aracın aktif olduğunu yaz.
2. GPower.exe'yi Ghidra ile içe aktar. Şu dizelere referans veren fonksiyonları bul:
   "Contingency", "Goodness-of-fit", "Total sample size", "Actual power",
   "Noncentrality parameter", "Critical", hata/uyarı mesajları.
3. Bu fonksiyonlardan geriye giderek şunları kanıtla. Her biri için fonksiyon adresi ve
   dize referansı ver; kanıt yoksa açıkça "kanıt yok" de:
   a) λ'nın nasıl hesaplandığı (N·w² mi?)
   b) a priori N aramasının algoritması: başlangıç değeri, adım, durma koşulu
      (güç ≥ hedef mi, > mı?), kesirli N'nin nasıl yuvarlandığı
   c) N alt ve üst sınırı
   d) güç ≤ α, w ≤ 0, α ∉ (0,1), kesirli df / kesirli N için tepki ve mesaj metni
   e) df'nin nereden okunduğu ve doğrulanıp doğrulanmadığı
4. Bulguları LEDGER.md §B tablosuna [REA] etiketiyle yaz. Kılavuzda zaten yazanları [DOK],
   kanıtlayamadıklarını [AJAN] olarak işaretle.
5. SPEC.md'yi yalnızca kanıta dayanarak güncelle; §9 "Açık sorular"ı kapat.
6. Emin olmadığın her iddiada dur ve "Bunun kanıtı hangi fonksiyonda?" sorusunu kendine sor.
Decompile edilmiş kod bloklarını hiçbir dosyaya kopyalama.
```
