# Uyum raporu (diferansiyel test)

Üretildi: 2026-10-21 14:01 · `python tests/diff_report.py`

## 1. G*Power arayüz vektörleri (asıl kâhin)

| id | kategori | girdi | G*Power | bizim | N | diğer | not |
|---|---|---|---|---|---|---|---|
| G01 | mutlu-yol | w=0.3 α=0.05 güç=0.8 df=1 | N=88 güç=0.8035275 | N=88 güç=0.8035275 | ✅ | ✅ | DOK vektörü: belgelenmiş N=88 |
| G02 | mutlu-yol | w=0.1 α=0.05 güç=0.8 df=1 | N=785 güç=0.8000569 | N=785 güç=0.8000569 | ✅ | ✅ | Cohen küçük etki |
| G03 | mutlu-yol | w=0.5 α=0.05 güç=0.8 df=1 | N=32 güç=0.8074304 | N=32 güç=0.8074304 | ✅ | ✅ | Cohen büyük etki |
| G04 | mutlu-yol | w=0.3 α=0.05 güç=0.95 df=5 | N=220 güç=0.9502155 | N=220 güç=0.9502155 | ✅ | ✅ | Kılavuz tarzı örnek |
| G05 | mutlu-yol | w=0.3 α=0.05 güç=0.9 df=2 | N=141 güç=0.9008626 | N=141 güç=0.9008626 | ✅ | ✅ | 2x3 tablo |
| G06 | mutlu-yol | w=0.3 α=0.01 güç=0.8 df=3 | N=172 güç=0.8007649 | N=172 güç=0.8007649 | ✅ | ✅ |  |
| G07 | mutlu-yol | w=0.2 α=0.05 güç=0.8 df=4 | N=299 güç=0.8009293 | N=299 güç=0.8009293 | ✅ | ✅ | 3x3 tablo |
| G08 | mutlu-yol | w=0.1 α=0.05 güç=0.95 df=1 | N=1300 güç=0.9500756 | N=1300 güç=0.9500756 | ✅ | ✅ |  |
| G09 | mutlu-yol | w=0.5 α=0.01 güç=0.99 df=1 | N=97 güç=0.9905779 | N=97 güç=0.9905779 | ✅ | ✅ |  |

**N tam eşleşme (a priori): 9/9 = 100.0%** (kapı: ≥ %90) · tüm alanlarda eşleşen: 9/9

## 2. Kılavuz / yayın örnekleri [DOK]

| id | girdi | beklenen N | bizim N | sonuç |
|---|---|---|---|---|
| D01 | w=0.3 α=0.05 güç=0.80 df=1 | 88 | 88 | ✅ |

## 3. Bağımsız kütüphane vektörleri (ölçek)

- Vektör sayısı: **630** (w × α × güç × df ızgarası)
- Motor N = ⌈kesirli N⌉ eşleşmesi: **630/630**
- Kesirli N'si bir tam sayıya 0,001'den yakın (yuvarlama açısından riskli) vektör: 1
- Not: kütüphane kesirli N verir (ör. 87,2), G*Power ve motor yukarı yuvarlar (88). Bu fark beklenen bir bulgudur; motor 'güç ≥ hedef olan en küçük tam sayı'yı arar (SPEC §3.3).

