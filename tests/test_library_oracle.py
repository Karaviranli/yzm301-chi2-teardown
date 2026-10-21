"""Ölçek katmanı: motor, bağımsız (Poisson serisi + sürekli kök) kâhinle eşleşmeli."""

import csv
import math
import pathlib
import sys

import pytest

from powerchi import engine

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "oracle"))
from independent_oracle import ncx2_sf_series, power_cont  # noqa: E402

ROWS = list(csv.DictReader((ROOT / "oracle" / "library_vectors.csv").open(encoding="utf-8")))


def test_has_500_plus_vectors():
    assert len(ROWS) >= 500


def test_all_library_vectors_match_ceil():
    bad = []
    for r in ROWS:
        n = engine.a_priori(float(r["w"]), float(r["alpha"]), float(r["power"]), int(r["df"])).n_total
        if n != int(r["n_ceil"]):
            bad.append((r["id"], n, r["n_ceil"]))
    assert not bad, bad[:10]


def test_ceil_of_fractional_is_reported_n():
    for r in ROWS:
        assert math.ceil(float(r["n_fractional"])) == int(r["n_ceil"])


@pytest.mark.parametrize("w,n,a,df", [(0.3, 88, 0.05, 1), (0.1, 1000, 0.01, 4), (1.0, 5, 0.05, 9), (0.05, 5000, 0.1, 2)])
def test_power_agrees_with_series(w, n, a, df):
    assert engine.power_at(w, n, a, df) == pytest.approx(power_cont(w, n, a, df), abs=1e-9)


def test_series_central_case():
    assert ncx2_sf_series(3.841458820694124, 1, 0.0) == pytest.approx(0.05)
