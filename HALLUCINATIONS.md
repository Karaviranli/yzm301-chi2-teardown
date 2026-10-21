# Halüsinasyon günlüğü

Ajanın yanlış çıkardığı şeyler, nasıl fark edildiği ve hangi testin yakaladığı. Kayıtlar gerçek olaylardır; uydurulmuş kayıt yoktur.

## Yazım oturumu (Oturum 2)

### H-01: "MCP sunucusu `from mcp.server.fastmcp import FastMCP` ile yazılır"
* **Ajanın iddiası:** MCP Python SDK'sında sunucu `FastMCP` sınıfıyla kurulur.
* **Gerçek:** Kurulu sürüm mcp 2.3.0. 2.x'te `FastMCP`, `mcp.server.mcpserver.MCPServer` olarak yeniden adlandırılmış. Eski içe aktarma `ModuleNotFoundError` veriyor.
* **Nasıl fark edildi:** İlk içe aktarma denemesi hata verdi. Hata mesajı geçiş kılavuzunu gösteriyordu.
* **Yakalayan test:** `tests/test_mcp_parity.py::test_tools_listed` (sunucu açılmadan araç listelenemez).
* **Ders:** Ajanın "bildiği" API, eğitim verisindeki sürümdür. Sürüm sabitlenir (`mcp>=2.3,<3`) ve doğrulanır.

### H-02: "Ajanın başlattığı MCP alt süreci `powerchi` paketini bulur"
* **Ajanın iddiası:** `python -m powerchi.mcp_server` alt süreç olarak her ortamda çalışır.
* **Gerçek:** Paket `pip install` ile kurulmadıysa alt süreç `PYTHONPATH`'i devralmıyor. Sonuç: `ModuleNotFoundError: No module named 'powerchi'` ve MCP bağlantısı "Connection closed".
* **Nasıl fark edildi:** Sahte LLM ile yazılan uçtan uca tesisat testi düştü.
* **Yakalayan test:** `tests/test_agent_plumbing.py::test_chi2_flow_numbers_come_from_engine`.
* **Düzeltme:** `agent.py` alt sürece paketin üst dizinini `PYTHONPATH` olarak geçiriyor.

### H-03 (kıl payı): "w=0,3, df=5, güç=0,95 → N=220 kılavuz örneğidir"
* **Ajanın iddiası:** Bu vektör G*Power kılavuzunda geçiyor.
* **Durum:** Ajan kaynak gösteremedi. Motor da 220 veriyor, ama motorun kendisiyle doğrulamak döngüsel olur. [DOK] yerine [AJAN] (A-01) olarak işaretlendi. G*Power ekranından G04 vektörüyle doğrulanacak.
* **Ders:** "Bunun kanıtı nerede?" sorusuna cevap yoksa satır [AJAN] olur.

## İnceleme oturumu (Oturum 1, REA)

Kâhin toplama (2026-10-21) sırasında ortaya çıkanlar. İlk üçü, yazım oturumundaki ajanın SPEC'e kanıtsız koyduğu kurallardır; dördüncüsü bu oturumdaki ajanın kendi hatasıdır.

### H-11: "Güç ≤ α ise a priori hata verir" (SPEC §6, eski)
* **Gerçek:** G*Power güç = α'yı kabul ediyor ve N = 1, actual power = 0,0603726 veriyor. Hata yalnızca güç < α için: "Power must be greater than or equal to alpha."
* **Nasıl fark edildi:** I01 ekranında hata penceresi çıkmadı. Önceki B06 sonucunun ekranda kalmış olabileceği şüphesiyle, araya başka bir hesap koyup I01 yeniden hesaplandı; sonuç aynı.
* **Yakalayan vektör:** I01 (I02 sınırın öbür tarafı). diff_report'ta N ❌.
* **Ders:** Mesaj metni ("greater than or equal") kuralı zaten söylüyordu; ajan "≤" ile "<" farkını kendi sezgisiyle doldurmuştu.

### H-12: "Kesirli df reddedilir" (SPEC §6, eski)
* **Gerçek:** G*Power df'yi en yakın tam sayıya yuvarlıyor, .5 yukarı gidiyor; df ≥ 1 kontrolü yuvarlamadan sonra. 1,5 → 2; 2,5 → 3; 0,6 → 1; 0,4 → hata.
* **Nasıl fark edildi:** I08'de (df=1,5) hata yerine N=108 geldi ve kritik χ² = 5,9914645, yani df=2 değeri. Kuralı ayırmak için E01–E05 vektörleri eklendi: 2,5 → 3 sonucu "çifte yuvarlama" (banker's) yorumunu eledi.
* **Yakalayan vektör:** I08, E01–E05.

### H-13: "Post hoc'ta kesirli N reddedilir" (SPEC §6, eski)
* **Gerçek:** G*Power N'yi en yakın tam sayıya yuvarlıyor: 50,5 → 51.
* **Yakalayan vektör:** P08.

### H-14: "Post hoc'ta N=50,5 yuvarlanmadan kullanılıyor" (bu oturumun ajanı)
* **Ajanın iddiası:** P08 ekranındaki λ = 4,59 değerini 50,5·0,09 sanıp CSV'ye "yuvarlanmadan kullanıldı" notu yazdı.
* **Gerçek:** 50,5·0,09 = 4,545; 4,59 = 51·0,09. Güç 0,5724114 da N=51'in gücü (scipy: N=50 → 0,5641, N=50,5 → 0,5683, N=51 → 0,5724).
* **Nasıl fark edildi:** Notu sınamak için üç N değerinde gücü bağımsız hesaplayınca ekrandaki değer yalnızca N=51 ile tuttu. Not, commit'ten önce düzeltildi.
* **Yakalayan vektör:** P08 (ekrandaki güç, 7 basamak).
* **Ders:** Ajanın zihinden yaptığı aritmetik de bir iddiadır; ekrandaki ikinci bir sayıyla (burada güç) çapraz kontrol edilmeden kanıt sayılmaz.
