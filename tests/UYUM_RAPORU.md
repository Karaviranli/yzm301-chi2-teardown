# Uyum raporu (diferansiyel test)

Üretildi: 2026-10-21 14:50 · `python tests/diff_report.py`

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
| G10 | mutlu-yol | w=0.3 α=0.1 güç=0.8 df=1 | N=69 güç=0.8015573 | N=69 güç=0.8015573 | ✅ | ✅ |  |
| G11 | mutlu-yol | w=0.25 α=0.05 güç=0.9 df=6 | N=279 güç=0.9003601 | N=279 güç=0.9003601 | ✅ | ✅ |  |
| G12 | mutlu-yol | w=0.4 α=0.05 güç=0.8 df=9 | N=98 güç=0.8009345 | N=98 güç=0.8009345 | ✅ | ✅ | 4x4 tablo |
| B01 | sinir-w-kucuk | w=0.01 α=0.05 güç=0.8 df=1 | N=78489 güç=0.8000020 | N=78489 güç=0.8000020 | ✅ | ✅ | d çok küçük karşılığı |
| B02 | sinir-w-kucuk | w=0.001 α=0.05 güç=0.8 df=1 | N=7848861 güç=0.8000000 | N=7848861 güç=0.8000000 | ✅ | ✅ | G*Power üst N sınırı var mı? |
| B03 | sinir-w-buyuk | w=2 α=0.05 güç=0.8 df=1 | N=2 güç=0.8074304 | N=2 güç=0.8074304 | ✅ | ✅ | N=2 bekleniyor |
| B04 | sinir-w-buyuk | w=3 α=0.05 güç=0.8 df=1 | N=1 güç=0.8508388 | N=1 güç=0.8508388 | ✅ | ✅ | N=1 mi? alt sınır testi (LEDGER L-07) |
| B05 | sinir-w-buyuk | w=5 α=0.05 güç=0.8 df=1 | N=1 güç=0.9988173 | N=1 güç=0.9988173 | ✅ | ✅ | N alt sınırı |
| B06 | sinir-guc | w=0.3 α=0.05 güç=0.051 df=1 | N=1 güç=0.0603726 | N=1 güç=0.0603726 | ✅ | ✅ | güç α'nın hemen üstünde |
| B07 | sinir-guc | w=0.3 α=0.05 güç=0.999 df=1 | N=284 güç=0.9990183 | N=284 güç=0.9990183 | ✅ | ✅ |  |
| B08 | sinir-alfa | w=0.3 α=0.001 güç=0.8 df=1 | N=190 güç=0.8008574 | N=190 güç=0.8008574 | ✅ | ✅ |  |
| B09 | sinir-alfa | w=0.3 α=0.5 güç=0.8 df=1 | N=24 güç=0.8027617 | N=24 güç=0.8027617 | ✅ | ✅ | büyük α |
| B10 | sinir-df | w=0.3 α=0.05 güç=0.8 df=20 | N=233 güç=0.8002286 | N=233 güç=0.8002286 | ✅ | ✅ |  |
| B11 | sinir-df | w=0.3 α=0.05 güç=0.8 df=50 | N=336 güç=0.8006734 | N=336 güç=0.8006734 | ✅ | ✅ |  |
| I01 | gecersiz | w=0.3 α=0.05 güç=0.05 df=1 | N=1 güç=0.0603726 | N=1 güç=0.0603726 | ✅ | ✅ | güç = α: G*Power ne yapıyor?; Hata yok: güç = α kabul edildi |
| I02 | gecersiz | w=0.3 α=0.05 güç=0.04 df=1 | Power must be greater than or equal to alpha. | power (0.04) alpha'dan (0.05) küçük olamaz | ✅ | ✅ | güç < α |
| I03 | gecersiz | w=0 α=0.05 güç=0.8 df=1 | Effect size w must be greater 1e-06. | a priori modda w 1e-06'dan büyük olmalı (verilen: 0.0) | ✅ | ✅ | w = 0 |
| I04 | gecersiz | w=-0.1 α=0.05 güç=0.8 df=1 | Effect size w must be greater 1e-06. | a priori modda w 1e-06'dan büyük olmalı (verilen: -0.1) | ✅ | ✅ | negatif w |
| I05 | gecersiz | w=0.3 α=0 güç=0.8 df=1 | Alpha is outside the admissible range (1e-07, 1). | alpha 0 ile 1 arasında (uçlar hariç) olmalı (verilen: 0.0) | ✅ | ✅ | α = 0 |
| I06 | gecersiz | w=0.3 α=1 güç=0.8 df=1 | Alpha is outside the admissible range (1e-07, 1). | alpha 0 ile 1 arasında (uçlar hariç) olmalı (verilen: 1.0) | ✅ | ✅ | α = 1 |
| I07 | gecersiz | w=0.3 α=0.05 güç=0.8 df=0 | Degrees of Freedom must be greater or equal one. | df en az 1 olmalı (verilen: 0, yuvarlanmış: 0) | ✅ | ✅ | df = 0 |
| I08 | gecersiz | w=0.3 α=0.05 güç=0.8 df=1.5 | N=108 güç=0.8036939 | N=108 güç=0.8036939 | ✅ | ✅ | kesirli df: G*Power yuvarlıyor mu, reddediyor mu?; Hata yok: df=1.5 → 2'ye yuvarlandı (kritik χ² df=2 değeri) |
| I09 | gecersiz | w=0.3 α=0.05 güç=1 df=1 | Power is outside the admissible range (1e-07, 1). | power 0 ile 1 arasında (uçlar hariç) olmalı (verilen: 1.0) | ✅ | ✅ | güç = 1 |
| P01 | post-hoc | w=0.3 α=0.05 N=88 df=1 | N=88 güç=0.8035275 | N=88 güç=0.8035275 | ✅ | ✅ | G01'in tersi |
| P02 | post-hoc | w=0.3 α=0.05 N=50 df=2 | N=50 güç=0.4604212 | N=50 güç=0.4604212 | ✅ | ✅ |  |
| P03 | post-hoc | w=0.1 α=0.05 N=100 df=1 | N=100 güç=0.1700750 | N=100 güç=0.1700750 | ✅ | ✅ |  |
| P04 | post-hoc | w=0.5 α=0.05 N=10 df=3 | N=10 güç=0.2330023 | N=10 güç=0.2330023 | ✅ | ✅ |  |
| P05 | post-hoc-sinir | w=0 α=0.05 N=100 df=1 | N=100 güç=0.0500000 | N=100 güç=0.0500000 | ✅ | ✅ | w=0: güç = α mı?; Hata yok: post hoc w=0 kabul edildi, λ ekranda '0' olarak gösterildi |
| P06 | post-hoc-sinir | w=0.3 α=0.05 N=1 df=1 | N=1 güç=0.0603726 | N=1 güç=0.0603726 | ✅ | ✅ | N=1 |
| P07 | post-hoc-gecersiz | w=0.3 α=0.05 N=0 df=1 | Total sample size is outside the admissible range (1, 2147483646) | n (toplam örneklem) 1 ile 2147483646 arasında olmalı (verile | ✅ | ✅ | N=0 |
| P08 | post-hoc-gecersiz | w=0.3 α=0.05 N=50.5 df=1 | N=50.5 güç=0.5724114 | N=51 güç=0.5724114 | ✅ | ✅ | kesirli N; Hata yok: N=50.5 → 51'e yuvarlandı (λ=4.59=51·0.09; güç = N=51 gücü) |
| E01 | kesirli-df | w=0.3 α=0.05 güç=0.8 df=1.4 | N=88 güç=0.8035275 | N=88 güç=0.8035275 | ✅ | ✅ | I08 sonrası eklendi: df yuvarlama kuralı; df=1.4 → 1 |
| E02 | kesirli-df | w=0.3 α=0.05 güç=0.8 df=1.6 | N=108 güç=0.8036939 | N=108 güç=0.8036939 | ✅ | ✅ | I08 sonrası eklendi: df yuvarlama kuralı; df=1.6 → 2 |
| E03 | kesirli-df | w=0.3 α=0.05 güç=0.8 df=2.5 | N=122 güç=0.8030869 | N=122 güç=0.8030869 | ✅ | ✅ | I08 sonrası eklendi: df yuvarlama kuralı; df=2.5 → 3 (yarım yukarı) |
| E04 | kesirli-df | w=0.3 α=0.05 güç=0.8 df=0.6 | N=88 güç=0.8035275 | N=88 güç=0.8035275 | ✅ | ✅ | I08 sonrası eklendi: df yuvarlama kuralı; df=0.6 → 1 (doğrulama yuvarlamadan sonra) |
| E05 | kesirli-df | w=0.3 α=0.05 güç=0.8 df=0.4 | Degrees of Freedom must be greater or equal one. | df en az 1 olmalı (verilen: 0.4, yuvarlanmış: 0) | ✅ | ✅ | I08 sonrası eklendi: df yuvarlama kuralı |

**N tam eşleşme (a priori): 37/37 = 100.0%** (kapı: ≥ %90) · tüm alanlarda eşleşen: 45/45

## 2. Kılavuz / yayın örnekleri [DOK]

| id | girdi | beklenen N | bizim N | sonuç |
|---|---|---|---|---|
| D01 | w=0.3 α=0.05 güç=0.80 df=1 | 88 | 88 | ✅ |

## 3. Bağımsız kütüphane vektörleri (ölçek)

- Vektör sayısı: **630** (w × α × güç × df ızgarası)
- Motor N = ⌈kesirli N⌉ eşleşmesi: **630/630**
- Kesirli N'si bir tam sayıya 0,001'den yakın (yuvarlama açısından riskli) vektör: 1
- Not: kütüphane kesirli N verir (ör. 87,2), G*Power ve motor yukarı yuvarlar (88). Bu fark beklenen bir bulgudur; motor 'güç ≥ hedef olan en küçük tam sayı'yı arar (SPEC §3.3).

