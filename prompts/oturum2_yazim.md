# Oturum 2: Yazım (temiz oda) · ilk prompt

> Yeni bir ajan oturumunda, YALNIZCA SPEC.md ile başlanır. Ghidra çıktısı, LEDGER'daki alıntılar ve GPower.exe bu oturuma verilmez.

```
Ekteki SPEC.md, χ² olumsallık tablosu güç analizinin davranış spesifikasyonudur.
Yalnızca bu belgeye dayanarak Python'da yeniden yaz:

- src/powerchi/engine.py : tek hesap motoru (a priori, post hoc, etki büyüklüğü, doğrulama).
  Dağılım fonksiyonları için scipy serbest; N çözücüsünü, yuvarlamayı ve df'yi kendin yaz.
- src/powerchi/cli.py    : SPEC §7'deki sözleşmeye birebir uyan ince CLI (gpower-clone).
- src/powerchi/mcp_server.py : aynı motoru çağıran ince MCP adaptörü; hesap mantığı kopyalanmaz.
- tests/ : SPEC §8'deki her Gherkin senaryosu için bir test; CLI'yi kara kutu olarak
  (alt süreçle) çalıştıran sözleşme testleri; MCP↔CLI parite testi.

SPEC'te olmayan bir davranış uydurma. Belirsizlik varsa SPEC §9'a soru olarak ekle.
Ürünü "G*Power" olarak adlandırma; README'de yazarlara atıf yap.
```

## Bu repodaki gerçek süreç notu

Bu repodaki kod, bir Claude oturumunda yazıldı. O oturum ödev yönergesini, slaytları ve **belgelenmiş** formülleri ([DOK]) gördü; Ghidra/decompile çıktısını hiç görmedi. SPEC.md o oturumda [DOK] kaynaklarından çıkarıldı. Kılavuzda olmayan davranışlar (§9) [REA] ile kapatıldıktan sonra SPEC güncellenir ve gerekiyorsa motor, yukarıdaki prompt ile **yeni** bir oturumda yalnızca SPEC.md'den düzeltilir. Bu düzeltme turunun kaydı AGENT_COST.md'ye eklenir.
