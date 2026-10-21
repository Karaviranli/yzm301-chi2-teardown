# Uyum raporu (diferansiyel test)

Üretildi: 2026-10-21 13:40 · `python tests/diff_report.py`

## 1. G*Power arayüz vektörleri (asıl kâhin)

> 40 vektörün girdileri hazır, G*Power çıktıları henüz girilmedi.
> `oracle/gpower_vectors.csv` dosyasındaki `gp_*` sütunlarını G*Power 3.1.9.7 ekranından doldurun
> ve ekran görüntüsünü `oracle/screenshots/<id>.png` olarak kaydedin. Sonra bu betiği yeniden çalıştırın.

## 2. Kılavuz / yayın örnekleri [DOK]

| id | girdi | beklenen N | bizim N | sonuç |
|---|---|---|---|---|
| D01 | w=0.3 α=0.05 güç=0.80 df=1 | 88 | 88 | ✅ |

## 3. Bağımsız kütüphane vektörleri (ölçek)

- Vektör sayısı: **630** (w × α × güç × df ızgarası)
- Motor N = ⌈kesirli N⌉ eşleşmesi: **630/630**
- Kesirli N'si bir tam sayıya 0,001'den yakın (yuvarlama açısından riskli) vektör: 1
- Not: kütüphane kesirli N verir (ör. 87,2), G*Power ve motor yukarı yuvarlar (88). Bu fark beklenen bir bulgudur; motor 'güç ≥ hedef olan en küçük tam sayı'yı arar (SPEC §3.3).

