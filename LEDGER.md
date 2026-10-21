# Kanıt defteri (LEDGER)

Etiketler: **[DOK]** kılavuz/makale/yayında yazıyor · **[REA]** binary'den kanıtlandı (fonksiyon adresi ya da dize referansıyla) · **[AJAN]** ajanın çıkarımı, kanıtı yok → diferansiyel testle sınanmalı.

Hedef: G*Power 3.1.9.7 (Windows), `GPowerNT.exe` SHA-256: `c63e6a13…c812` (README) · İnceleme aracı: REA (`rea-agents`), Ghidra + JDK 21.

> **Durum:** [DOK] ve [AJAN] satırları dolduruldu. [REA] satırları, inceleme oturumu (prompts/oturum1_inceleme.md) GPower.exe üzerinde çalıştırılınca doldurulacak. Hiçbir [REA] satırı tahminle yazılmamıştır; yazılmamalıdır.

## A. Belgelenmiş davranış [DOK]

| ID | İddia | Kaynak | Test |
|---|---|---|---|
| L-01 | w=0,3, df=1, α=0,05, güç=0,80 → toplam N = 88 | Newsom, *Power analysis examples* (Portland State Univ.), G*Power "Goodness of fit" ekranı. oracle/dok_vectors.csv D01 | `test_documented_vector_n88`, diff_report §2 |
| L-02 | Etki büyüklüğü w ile λ = N·w² | Faul vd. (2007) G*Power 3 makalesi; G*Power 3.1 kılavuzu, χ² testleri bölümü | `test_ncp_formula` |
| L-03 | Güç, noncentral χ²(df, λ) dağılımının merkezi χ² kritik değerin üstündeki kuyruğudur | Faul vd. (2007); Cohen (1988) bölüm 7 | `test_power_agrees_with_series` |
| L-04 | df = (satır−1)(sütun−1) | Kılavuz / standart istatistik | `test_w_three_groups_df` |
| L-10 | w = √Σ(p1−p0)²/p0; olumsallıkta p0 = marjinallerin çarpımı | Cohen (1988) §7.2; kılavuzdaki "Determine" penceresi | `test_w_from_table_*` |

## B. Kılavuzda OLMAYAN davranış: [REA] ile kanıtlanacak

Puan bu bölümden gelir. Her satır için: fonksiyon adresi (`FUN_00xxxxxx` ya da sembol), dize referansı (adres + kısa alıntı), güven ve hâlâ bilinmeyen.

| ID | İddia (hipotez) | [REA] kanıtı (adres / dize) | Güven | Bilinmeyen | Doğrulayan vektör |
|---|---|---|---|---|---|
| L-05 | A priori N yukarı yuvarlanır (en küçük tam sayı, güç ≥ hedef) | *doldurulacak* | — | Hep yukarı mı? | G01–G12, library 630 |
| L-06 | Durma koşulu: güç ≥ hedef (eşitlik dahil) | *doldurulacak* | — | Tam sayı taraması mı, kesirli kök + ceil mi? | B06, B07 |
| L-07 | N araması 1'den başlar | *doldurulacak* | — | G*Power'ın alt sınırı 2 ya da df+1 olabilir | B03, B04, B05 |
| L-08 | N için üst sınır yok / var | *doldurulacak* | — | Çok küçük w'de ne gösteriyor? | B01, B02 |
| L-11 | güç ≤ α → hata | *doldurulacak* (hata dizesi) | — | Mesaj metni ne? | I01, I02 |
| L-12 | w ≤ 0, α ∉ (0,1), güç ≥ 1 → hata | *doldurulacak* | — | Alan kırmızı mı oluyor, sessizce mi düzeltiliyor? | I03–I06, I09 |
| L-13 | Kesirli df / kesirli N reddedilir | *doldurulacak* | — | Yuvarlıyor olabilir | I07, I08, P08 |
| L-09 | Post hoc w=0 → güç = α | *doldurulacak* | — | — | P05 |

## C. Ajan çıkarımları [AJAN]: kanıt yok, testle sınanıyor

| ID | Çıkarım | Neden şüpheli | Durum |
|---|---|---|---|
| A-01 | G04 (w=0,3, df=5, α=0,05, güç=0,95 → N=220) "kılavuzdaki örnek" | Yazım oturumundaki ajan bunu bellekten hatırladı, kaynak gösteremedi | [DOK]'a alınmadı; G*Power ekranından G04 ile doğrulanacak |
| A-02 | Çıktı 4 ondalığa yuvarlanır | Sözleşme örneği 4 basamak kullanıyor; G*Power ekranı daha fazla basamak gösterebilir | diff_report, G*Power'ın gösterdiği basamağa göre karşılaştırır (`--precision 7`) |
| A-03 | `--tails` χ² için yok sayılmalı | Değerlendirme düzeneği tüm ailelere aynı bayrakları gönderebilir | Sözleşme testi var; hocaya sorulabilir |

## D. Eşleme: kural → test

| Kural (SPEC) | Kanıt | Test |
|---|---|---|
| §2 model | L-01…L-04 | test_engine, test_library_oracle |
| §3.3 yuvarlama | L-05 | test_minimal_n, library 630/630 |
| §3.4 alt sınır | L-07 | test_lower_bound_n, B03–B05 |
| §4 post hoc | L-09 | test_post_hoc_* |
| §5 etki büyüklüğü | L-10 | test_w_* |
| §6 geçersiz girdi | L-11…L-13 | test_invalid_*, test_cli_contract |
| §7 sözleşme | yönerge | test_cli_contract, test_mcp_parity |
