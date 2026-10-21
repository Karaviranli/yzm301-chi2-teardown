"""İnce MCP adaptörü (stdio). Hesap mantığı YOKTUR; yalnızca engine'i çağırır.

Çalıştır:   python -m powerchi.mcp_server        (ya da kurulumdan sonra: powerchi-mcp)
Gerekir:    pip install "mcp>=2.3,<3"

Araçlar (şema README §MCP'de):
  chi2_contingency_power  -> CLI'deki a-priori / post-hoc çıktısının AYNISI
  chi2_effect_size        -> CLI'deki effect-size çıktısının AYNISI
"""

from __future__ import annotations

from typing import Optional

from mcp.server.mcpserver import MCPServer

from . import engine

server = MCPServer(
    name="powerchi",
    instructions=(
        "χ² olumsallık tablosu (contingency table) için istatistiksel güç analizi. "
        "Sayıları ASLA kendin hesaplama; N, güç ve w her zaman bu araçlardan gelmeli. "
        "Yanıt oranları biliniyorsa önce chi2_effect_size ile w'yi bul, sonra chi2_contingency_power'ı çağır."
    ),
)


@server.tool(
    name="chi2_contingency_power",
    description=(
        "Chi-square test for contingency tables (G*Power: 'Goodness-of-fit tests: Contingency tables'). "
        "mode='a-priori' -> required total sample size N for target power; "
        "mode='post-hoc' -> achieved power for a given total N. "
        "df = (rows-1)*(cols-1); for k groups x binary response df = k-1. Fractional df and n are rounded to the nearest integer (.5 up). "
        "Returns the exact same JSON as the gpower-clone CLI, or {'error': ...}."
    ),
)
def chi2_contingency_power(mode: str, w: float, alpha: float, df: float,
                           power: Optional[float] = None, n: Optional[float] = None) -> dict:
    try:
        return engine.compute(mode, w=w, alpha=alpha, power=power, df=df, n=n)
    except engine.InputError as e:
        return {"error": str(e)}


@server.tool(
    name="chi2_effect_size",
    description=(
        "Cohen's w effect size for a contingency table. Either give 'rates' (response/success rate of each "
        "group, 0..1) with optional 'weights' (relative group sizes, default equal), or give 'table' "
        "(H1 cell probabilities or counts, list of rows). Returns {'w','df','rows','cols'} or {'error': ...}."
    ),
)
def chi2_effect_size(rates: Optional[list[float]] = None, weights: Optional[list[float]] = None,
                     table: Optional[list[list[float]]] = None) -> dict:
    try:
        if table:
            return engine.w_from_table(table).to_dict()
        if rates:
            return engine.w_from_rates(rates, weights).to_dict()
        return {"error": "rates ya da table gerekli"}
    except engine.InputError as e:
        return {"error": str(e)}


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
