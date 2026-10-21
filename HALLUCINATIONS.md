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

REA/Ghidra oturumunda ajanın yanlış çıkardıkları buraya aynı biçimde eklenecek. Bakılacak tipik yerler:

* Ajanın "N'yi ceil ile yuvarlıyor" deyip adres gösteremediği yerler (L-05)
* Hata mesajı dizesinin hangi koşula bağlı olduğu (L-11 … L-13)
* t-testi ailesine ait bir fonksiyonu χ² hesabı sanması (aile karışıklığı)

| ID | İddia | Gerçek | Nasıl fark edildi | Yakalayan test/vektör |
|---|---|---|---|---|
| H-1x | | | | |
