"""500+ ölçek vektörü üretir: oracle/library_vectors.csv

Çalıştır:  python oracle/gen_library_vectors.py
"""

from __future__ import annotations

import csv
import itertools
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from independent_oracle import n_fractional, power_cont, statsmodels_n  # noqa: E402

W = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.7, 1.0]
ALPHA = [0.01, 0.05, 0.10]
POWER = [0.80, 0.90, 0.95]
DF = [1, 2, 3, 4, 5, 6, 9]


def main() -> None:
    out = HERE / "library_vectors.csv"
    rows = 0
    with out.open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["id", "w", "alpha", "power", "df", "n_fractional", "n_ceil",
                     "power_at_ceil", "statsmodels_n_fractional", "source"])
        for i, (w, a, p, df) in enumerate(itertools.product(W, ALPHA, POWER, DF), 1):
            nf = n_fractional(w, a, p, df)
            nc = math.ceil(nf)
            sm = statsmodels_n(w, a, p, df)
            wr.writerow([f"L{i:04d}", w, a, p, df, f"{nf:.6f}", nc,
                         f"{power_cont(w, nc, a, df):.7f}",
                         "" if sm is None else f"{sm:.6f}",
                         "independent-series" + ("+statsmodels" if sm is not None else "")])
            rows += 1
    print(f"{rows} vektör yazıldı -> {out}")


if __name__ == "__main__":
    main()
