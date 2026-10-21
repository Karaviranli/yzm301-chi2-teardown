# SPEC: χ² testi, olumsallık tablosu (K4)

**Hedef davranış:** G*Power 3.1.9.7 (Windows) → *Test family: χ² tests* → *Statistical test: Goodness-of-fit tests: Contingency tables*
**Modlar:** A priori (N hesapla), Post hoc (gücü hesapla). Ek olarak etki büyüklüğü (w) yardımcısı.
**Kaynak etiketleri:** Her kural LEDGER.md'deki bir satıra bağlıdır (`L-xx`). [REA] satırı olmayan kurallar diferansiyel testle doğrulanana kadar *hipotez* sayılır.

> Bu belge yeniden yazım oturumunun TEK girdisidir (temiz oda). Decompile çıktısı içermez.

---

## 1. Sözlük

| Terim | Anlam |
|---|---|
| w | Cohen etki büyüklüğü: `w = √ Σ (p1ᵢ − p0ᵢ)² / p0ᵢ` |
| df | Serbestlik derecesi. r×c tablo için `(r − 1)(c − 1)`; k grup × evet/hayır için `k − 1` |
| α | I. tip hata olasılığı |
| güç | 1 − β |
| λ (ncp) | Noncentrality parametresi |
| N | Toplam örneklem (tüm hücrelerin toplamı) |

## 2. Model (L-01 … L-04)

```
λ      = N · w²
χ²_c   = merkezi χ²(df) dağılımının üst α kantili
güç(N) = P( χ'²(df, λ) > χ²_c )        χ'² : noncentral χ²
```

## 3. A priori çözücü (L-05 … L-08)

3.1 Girdi: w, α, hedef güç, df.
3.2 Güç, N'de monoton artandır.
3.3 **Çıktı N = güç(N) ≥ hedef olan en küçük tam sayı** (kesirli N yukarı yuvarlanır; hiçbir zaman aşağı değil).
3.4 Arama alt sınırı `N_MIN = 1`. Kâhinle doğrulandı: w=3 ve w=5 → N=1 (B04, B05); güç=0,051 → N=1 (B06).
3.5 N 10⁸'i aşacaksa hata döner. (G*Power w=0,001 için N=7 848 861 veriyor (B02); bu sınırın altında.)
3.6 "Actual power" = güç(N) (hedef değil, bulunan N'deki gerçek güç).
3.7 **güç = α kabul edilir** (hata değildir). Arama 3.3'teki kuralla çalışır; güç(1) > α olduğundan sonuç N = 1'dir (I01: w=0,3, α=0,05, güç=0,05 → N=1, actual power 0,0603726).

## 4. Post hoc (L-09)

Girdi: w, α, N, df. Çıktı: güç(N), χ²_c, λ. w = 0 kabul edilir ve güç = α olur (P05).
**Kesirli N, en yakın tam sayıya yuvarlanır (yarım yukarı)** ve hesap bu tam sayıyla yapılır: N=50,5 → 51; λ = 4,59, güç = 0,5724114 (P08). Yuvarlanmış N, `n_total` alanında döner.
N geçerli aralığı: 1 ≤ N ≤ 2 147 483 646 (P07 mesajı).

## 4b. df'nin yorumlanması (a priori ve post hoc)

**Kesirli df, en yakın tam sayıya yuvarlanır; .5 yukarı gider.** Doğrulama (df ≥ 1) yuvarlamadan SONRA yapılır. Çıktıdaki `df` yuvarlanmış değerdir.

| girdi df | kullanılan df | kâhin |
|---|---|---|
| 0,4 | 0 → hata | E05 |
| 0,6 | 1 | E04 (N=88) |
| 1,4 | 1 | E01 (N=88) |
| 1,5 | 2 | I08 (N=108) |
| 1,6 | 2 | E02 (N=108) |
| 2,5 | 3 | E03 (N=122) |

## 5. Etki büyüklüğü (L-10)

* Tablo girdisi (olasılık ya da frekans; toplama bölünerek normalize edilir). H0 hücreleri marjinallerin çarpımıdır: `p0ᵢⱼ = rᵢ · cⱼ`.
* Oran girdisi: k grubun yanıt oranı + (isteğe bağlı) grup payları → k×2 tablo.

## 6. Geçersiz girdi (L-11 … L-13)

Kaynak: G*Power ekranındaki "Input error" pencereleri (oracle/screenshots/). G*Power'ın mesaj metni karşılaştırma için yanda verilmiştir; motorun mesajı farklı olabilir, yalnızca hata/hata-değil ayrımı ve çıkış kodu sözleşmedir.

| Koşul | Davranış | G*Power mesajı | Kâhin |
|---|---|---|---|
| w sayı değil / NaN / ∞ | hata | — | — |
| a priori: w ≤ 1e-6 (w = 0 ve negatif w dahil) | hata | "Effect size w must be greater 1e-06." | I03, I04 |
| post hoc: w < 0 | hata | — | — |
| post hoc: w = 0 | **geçerli**, güç = α | — | P05 |
| α ∉ (0, 1) | hata | "Alpha is outside the admissible range (1e-07, 1)." | I05, I06 |
| güç ∉ (0, 1) | hata | "Power is outside the admissible range (1e-07, 1)." | I09 |
| güç < α (a priori) | hata | "Power must be greater than or equal to alpha." | I02 |
| güç = α (a priori) | **geçerli**, §3.7 | — | I01 |
| yuvarlanmış df < 1 (§4b) | hata | "Degrees of Freedom must be greater or equal one." | I07, E05 |
| kesirli df | **geçerli**, §4b'ye göre yuvarlanır | — | I08, E01–E04 |
| post hoc: yuvarlanmış N < 1 | hata | "Total sample size is outside the admissible range (1, 2147483646)" | P07 |
| post hoc: kesirli N | **geçerli**, §4'e göre yuvarlanır | — | P08 |
| tablo 2×2'den küçük, düzensiz, negatif hücre, sıfır satır/sütun | hata | — | — |

## 7. CLI sözleşmesi (L-14)

```
gpower-clone --test chi2-contingency --mode a-priori --w W --alpha A --power P --df D
gpower-clone --test chi2-contingency --mode post-hoc --w W --alpha A --n N --df D
gpower-clone --test chi2-contingency --mode effect-size (--rates r1,r2[,..] [--weights a,b,..] | --table "a,b;c,d")
```

* Başarı: stdout'a tek satır JSON, çıkış kodu 0. Sayılar 4 ondalığa yuvarlanır (`--precision` ile değişir).
* A priori anahtar sırası: `n_total, actual_power, critical, df, ncp`
* Post hoc anahtar sırası: `n_total, power, critical, df, ncp`
* Hata: `{"error":"<açıklama>"}`, çıkış kodu 2.
* `--tails` ve `--ratio` (diğer ailelerin bayrakları) kabul edilir ve yok sayılır. Ondalık virgül (`0,3`) kabul edilir.

---

## 8. Kabul kriterleri (Gherkin)

```gherkin
Feature: A priori örneklem büyüklüğü

  Background:
    Given test "chi2-contingency"

  # S-01  [DOK] L-01
  Scenario: Belgelenmiş vektör
    When mode "a-priori", w 0.3, alpha 0.05, power 0.80, df 1
    Then n_total 88
    And critical 3.8415
    And ncp 7.92
    And actual_power ≥ 0.80

  # S-02  L-05 (yuvarlama)
  Scenario Outline: N hedef güce ulaşan en küçük tam sayıdır
    When mode "a-priori", w <w>, alpha <a>, power <p>, df <df>
    Then actual_power ≥ <p>
    And güç(n_total − 1) < <p>
    Examples:
      | w    | a    | p    | df |
      | 0.3  | 0.05 | 0.80 | 1  |
      | 0.1  | 0.05 | 0.95 | 1  |
      | 0.3  | 0.05 | 0.95 | 5  |
      | 0.25 | 0.01 | 0.90 | 6  |

  # S-03  L-02
  Scenario: Noncentrality
    When mode "post-hoc", w 0.25, alpha 0.05, n 160, df 3
    Then ncp 10.0

  # S-08  L-07 (alt sınır; kâhin B04)
  Scenario: Çok büyük etki
    When mode "a-priori", w 3, alpha 0.05, power 0.80, df 1
    Then n_total 1

  # S-10  §3.7 (kâhin I01)
  Scenario: Güç α'ya eşitse hata değildir
    When mode "a-priori", w 0.3, alpha 0.05, power 0.05, df 1
    Then n_total 1
    And actual_power 0.0603726 (7 basamakta)

  # S-11  §4b (kâhin I08, E01–E04)
  Scenario Outline: Kesirli df en yakın tam sayıya yuvarlanır, .5 yukarı
    When mode "a-priori", w 0.3, alpha 0.05, power 0.80, df <df>
    Then df <dfk> and n_total <n>
    Examples:
      | df  | dfk | n   |
      | 0.6 | 1   | 88  |
      | 1.4 | 1   | 88  |
      | 1.5 | 2   | 108 |
      | 1.6 | 2   | 108 |
      | 2.5 | 3   | 122 |

  # S-09
  Scenario: df arttıkça N artar
    When aynı w=0.3, alpha=0.05, power=0.80 için df 1, 2, 4, 8
    Then n_total kesin artan bir dizidir

Feature: Post hoc güç

  # S-05
  Scenario: Post hoc a priori'nin tersidir
    Given a priori w 0.3, alpha 0.05, power 0.90, df 2 → N
    When mode "post-hoc" aynı w, alpha, df ve n N
    Then power = a priori actual_power

  # S-06  L-09
  Scenario: Etki yoksa güç α'dır
    When mode "post-hoc", w 0, alpha 0.05, n 100, df 1
    Then power 0.05

  # S-12  §4 (kâhin P08)
  Scenario: Kesirli N en yakın tam sayıya yuvarlanır
    When mode "post-hoc", w 0.3, alpha 0.05, n 50.5, df 1
    Then n_total 51 and ncp 4.59 and power 0.5724114 (7 basamakta)

Feature: Etki büyüklüğü

  # L-10
  Scenario: Eşit iki grup, %60 vs %40
    When mode "effect-size", rates 0.6,0.4
    Then w 0.2 and df 1

  Scenario: Bağımsız tablo
    When table "0.06,0.14;0.24,0.56"
    Then w 0

Feature: Geçersiz girdi

  # L-11 … L-13
  Scenario Outline: Hata nesnesi ve sıfırdan farklı çıkış kodu
    When <girdi>
    Then stdout tek satır {"error": "..."} ve çıkış kodu ≠ 0
    Examples:
      | girdi                                   |
      | a-priori, power < alpha (0.04 < 0.05)   |
      | a-priori, w = 0                         |
      | a-priori, w = -0.1                      |
      | post-hoc, w = -0.1                      |
      | alpha = 0 ya da 1                       |
      | power = 1                               |
      | df = 0 ya da 0.4 (yuvarlanınca 0)       |
      | post-hoc, n = 0 ya da 0.4               |
      | eksik parametre, bilinmeyen bayrak      |
      | bilinmeyen mod ya da test ailesi        |

Feature: Ölçek ve parite

  Scenario: Bağımsız kütüphane kâhini
    Given oracle/library_vectors.csv içindeki 630 vektör
    Then her biri için n_total = ⌈kesirli N⌉

  Scenario: MCP ↔ CLI
    Given aynı girdi
    Then MCP aracının JSON çıktısı CLI çıktısıyla birebir aynıdır (hata mesajları dahil)
```

## 9. Açık sorular

Kâhinle (G*Power ekranı, 2026-10-21) kapatılanlar:

1. ~~N aramasına kaçtan başlıyor?~~ N = 1 (B04, B05, B06, I01). §3.4.
2. ~~Güç ≤ α, w = 0, kesirli df, kesirli N?~~ güç < α hata, güç = α geçerli; a priori w ≤ 1e-6 hata, post hoc w = 0 geçerli; kesirli df ve kesirli N en yakın tam sayıya yuvarlanır. §3.7, §4, §4b, §6.
3. ~~N üst sınırı?~~ w = 0,001 için N = 7 848 861 hesaplanıyor (B02); pratik vektörlerde üst sınıra takılma yok.

Açık kalan:

4. Durma koşulu: kesirli kök + `ceil` mi, tam sayı taraması mı? Kâhinin 23 a priori vektörü ve 630 kütüphane vektörü iki yorumda da aynı N'yi veriyor; fark yalnızca güç(N) hedefe 1e-10 mertebesinde eşit olduğunda görülebilir. Motor tam sayı taramasında kalır.
