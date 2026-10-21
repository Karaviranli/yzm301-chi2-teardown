"""Türkçe klinik soru → MCP aracı → yanıt veren ajan (bonus +10).

Akış (README §Ajan):
  1. Sistem 1 (hızlı karar): soru yalnızca etiket setine kısıtlı bir LLM çağrısıyla
     sınıflandırılır: t2-indep, t-paired, anova-oneway, chi2-contingency,
     multireg-r2, ambiguous, unsupported  + güven (0..1).
     Güven < 0,75 ya da etiket ambiguous/unsupported ise karar ARAŞTIRMACIYA sorulur.
     Bu adım HİÇBİR sayı üretmez.
  2. Sistem 2: etiket chi2-contingency ise model parametreleri çıkarır ve MCP
     araçlarını (chi2_effect_size, chi2_contingency_power) çağırır. N/güç/w her
     zaman araç sonucundan gelir; ajan hesap YAPMAZ.
  3. Her çağrı logs/agent_calls.jsonl'e (araç girdisi/çıktısı, token kullanımı, süre) yazılır.

Gereksinim: ANTHROPIC_API_KEY ortam değişkeni ve `pip install "mcp>=2.3,<3"`.
Dış bağımlılık olarak yalnızca standart kütüphane (urllib) kullanılır.

Kullanım:
  python -m powerchi.agent "Yeni ilaçta yanıt oranı %75, standartta %60. %80 güç, α=0,05 için kaç hasta?"
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import sys
import time
import urllib.request
from dataclasses import dataclass, field

API_URL = "https://api.anthropic.com/v1/messages"
CLASSIFIER_MODEL = os.environ.get("POWERCHI_CLASSIFIER_MODEL", "claude-haiku-5-5")
AGENT_MODEL = os.environ.get("POWERCHI_AGENT_MODEL", "claude-sonnet-5-5")
LABELS = ["t2-indep", "t-paired", "anova-oneway", "chi2-contingency", "multireg-r2", "ambiguous", "unsupported"]
CONF_THRESHOLD = 0.75
SUPPORTED = {"chi2-contingency"}
LOG_DIR = pathlib.Path(os.environ.get("POWERCHI_LOG_DIR", "logs"))

CLASSIFIER_SYSTEM = f"""Sen bir test ailesi sınıflandırıcısısın. Bir hekimin Türkçe (ya da İngilizce) güç analizi sorusunu
okuyup YALNIZCA şu etiketlerden birini seç: {", ".join(LABELS)}.
- chi2-contingency: kategorik sonuç; gruplar arası oran/yüzde/yanıt oranı karşılaştırması, olumsallık tablosu, w etki büyüklüğü
- t2-indep: iki bağımsız grubun sürekli ölçüm ortalaması (d)
- t-paired: aynı deneklerde önce/sonra ortalama
- anova-oneway: üç+ grubun sürekli ölçüm ortalaması (f)
- multireg-r2: çoklu regresyon, R², risk faktörleri sayısı
- ambiguous: aile belirlenebilir ama hangi test olduğu ya da zorunlu bilgi belirsiz
- unsupported: güç analizi sorusu değil ya da bu listede olmayan bir test
Hiçbir sayı hesaplama. Yalnızca JSON döndür: {{"label": "<etiket>", "confidence": <0..1>, "reason": "<kısa>"}}"""

AGENT_SYSTEM = """Sen klinik araştırmacılara χ² olumsallık tablosu güç analizinde yardım eden bir asistansın.
KURALLAR:
1. N, güç, kritik değer, λ ve w değerlerini ASLA kendin hesaplama veya tahmin etme. Her sayı bir araç sonucundan gelmeli.
2. Yanıt oranları verildiyse önce chi2_effect_size aracını çağır (rates; gruplar eşit değilse weights). Sonra dönen w ve df ile chi2_contingency_power'ı çağır.
3. w doğrudan verildiyse df'yi tablo boyutundan bul: df = (satır-1)(sütun-1); k grup × evet/hayır için df = k-1.
4. N isteniyorsa mode="a-priori" (power gerekli), elde edilen güç isteniyorsa mode="post-hoc" (n gerekli).
5. α verilmemişse 0,05 kabul et ve bunu yanıtında açıkça söyle. Güç verilmemişse 0,80 kabul et ve söyle.
6. Zorunlu bilgi eksikse (ör. oranlar da w de yoksa) araç çağırma; araştırmacıya kısa bir soru sor.
7. Yanıtı Türkçe, 2-4 cümle ver: toplam N (ya da güç), kullanılan w, df, α ve varsayımlar."""


# --------------------------------------------------------------------------
# Anthropic Messages API (standart kütüphane ile)
# --------------------------------------------------------------------------

def _post(payload: dict) -> dict:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY tanımlı değil")
    req = urllib.request.Request(API_URL, data=json.dumps(payload).encode("utf-8"), method="POST",
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                          "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0

    def add(self, u: dict) -> None:
        self.input_tokens += u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + \
            u.get("cache_creation_input_tokens", 0)
        self.output_tokens += u.get("output_tokens", 0)
        self.calls += 1


@dataclass
class AgentResult:
    question: str
    label: str
    confidence: float
    asked_researcher: bool
    answer: str
    tool_calls: list = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)
    seconds: float = 0.0

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        d["usage"] = self.usage.__dict__
        return d


def classify(question: str, usage: Usage) -> tuple[str, float, str]:
    resp = _post({"model": CLASSIFIER_MODEL, "max_tokens": 200, "system": CLASSIFIER_SYSTEM,
                  "messages": [{"role": "user", "content": question}]})
    usage.add(resp.get("usage", {}))
    text = "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text").strip()
    try:
        obj = json.loads(text[text.index("{"): text.rindex("}") + 1])
        label = obj.get("label", "unsupported")
        conf = float(obj.get("confidence", 0))
        reason = obj.get("reason", "")
    except (ValueError, json.JSONDecodeError):
        label, conf, reason = "ambiguous", 0.0, f"sınıflandırıcı çıktısı okunamadı: {text[:80]}"
    if label not in LABELS:  # etiket setine kısıtlama
        label, conf = "unsupported", 0.0
    return label, conf, reason


# --------------------------------------------------------------------------
# Ajan döngüsü (MCP araçlarıyla)
# --------------------------------------------------------------------------

def _payload(result) -> dict:
    sc = getattr(result, "structured_content", None) or getattr(result, "structuredContent", None)
    if sc:
        return sc.get("result", sc) if set(sc) == {"result"} else sc
    return json.loads(result.content[0].text)


async def _run_tools(question: str, res: AgentResult, max_turns: int = 6) -> None:
    import mcp
    from mcp import StdioServerParameters

    # Paket pip ile kurulmamış olsa da alt süreç powerchi'yi bulabilsin
    pkg_parent = str(pathlib.Path(__file__).resolve().parents[1])
    env = dict(os.environ)
    env["PYTHONPATH"] = pkg_parent + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    params = StdioServerParameters(command=sys.executable, args=["-m", "powerchi.mcp_server"], env=env)
    async with mcp.Client(params) as client:
        listed = (await client.list_tools()).tools
        tools = []
        for t in listed:
            schema = getattr(t, "input_schema", None) or getattr(t, "inputSchema")
            tools.append({"name": t.name, "description": t.description or "", "input_schema": schema})
        messages = [{"role": "user", "content": question}]
        for _ in range(max_turns):
            resp = _post({"model": AGENT_MODEL, "max_tokens": 800, "system": AGENT_SYSTEM,
                          "tools": tools, "messages": messages})
            res.usage.add(resp.get("usage", {}))
            content = resp.get("content", [])
            messages.append({"role": "assistant", "content": content})
            uses = [b for b in content if b.get("type") == "tool_use"]
            if not uses:
                res.answer = "".join(b.get("text", "") for b in content if b.get("type") == "text").strip()
                return
            results = []
            for u in uses:
                t0 = time.time()
                out = _payload(await client.call_tool(u["name"], u["input"]))
                res.tool_calls.append({"tool": u["name"], "input": u["input"], "output": out,
                                       "ms": round(1000 * (time.time() - t0), 1)})
                results.append({"type": "tool_result", "tool_use_id": u["id"],
                                "content": json.dumps(out, ensure_ascii=False)})
            messages.append({"role": "user", "content": results})
        res.answer = "(tur sınırı aşıldı)"


def ask(question: str) -> AgentResult:
    t0 = time.time()
    res = AgentResult(question=question, label="", confidence=0.0, asked_researcher=False, answer="")
    label, conf, reason = classify(question, res.usage)
    res.label, res.confidence = label, conf
    if label in ("ambiguous", "unsupported") or conf < CONF_THRESHOLD:
        res.asked_researcher = True
        res.answer = (f"Bu sorunun hangi teste karşılık geldiğinden emin değilim (etiket: {label}, güven: {conf:.2f}; "
                      f"{reason}). Sonucunuz kategorik mi (oran/yüzde) yoksa sürekli bir ölçüm mü? "
                      f"Grup sayısını ve beklenen oranları belirtir misiniz?")
    elif label not in SUPPORTED:
        res.answer = (f"Bu soru '{label}' ailesine ait görünüyor (güven {conf:.2f}). Bu araç yalnızca χ² olumsallık "
                      f"tablosunu hesaplar; bu soru için ilgili ailenin aracını kullanın.")
    else:
        asyncio.run(_run_tools(question, res))
    res.seconds = round(time.time() - t0, 2)
    _log(res)
    return res


def _log(res: AgentResult) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with (LOG_DIR / "agent_calls.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "classifier": CLASSIFIER_MODEL,
                            "agent": AGENT_MODEL, **res.to_dict()}, ensure_ascii=False) + "\n")


def main() -> int:
    if len(sys.argv) < 2:
        print('kullanım: python -m powerchi.agent "<klinik soru>"', file=sys.stderr)
        return 2
    try:
        r = ask(" ".join(sys.argv[1:]))
    except RuntimeError as e:
        print(f"hata: {e}", file=sys.stderr)
        return 2
    print(r.answer)
    print(json.dumps({"label": r.label, "confidence": r.confidence, "tool_calls": r.tool_calls,
                      "usage": r.usage.__dict__, "seconds": r.seconds}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
