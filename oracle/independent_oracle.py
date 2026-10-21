"""Bağımsız kütüphane kâhini (ölçek katmanı).

Motordan BAĞIMSIZ bir yoldan güç ve kesirli N hesaplar:
  * noncentral χ² kuyruğu scipy.stats.ncx2 yerine Poisson karışımı serisiyle
    (Σ Pois(k; λ/2) · Q(df/2 + k, c/2)) hesaplanır,
  * N, R'daki pwr.chisq.test gibi SÜREKLİ bir kök bulma ile (kesirli) bulunur,
    sonra tavanı alınır.

İki farklı algoritma aynı sonucu verirse motorun dağılım katmanına güven artar.
Ama bu katman G*Power'ın YERİNE geçmez: yuvarlama ve kenar durum davranışını
yalnızca G*Power'ın kendisi (oracle/gpower_vectors.csv) belirler.

statsmodels kuruluysa (pip install statsmodels) aynı vektörler ayrıca
statsmodels.stats.power.GofChisquarePower ile de çözülür. DİKKAT: statsmodels
`n_bins` parametresi alır ve df = n_bins - 1 kullanır.
"""

from __future__ import annotations

import math

from scipy.special import gammaincc
from scipy.stats import chi2


def ncx2_sf_series(x: float, df: int, lam: float, tol: float = 1e-15) -> float:
    """P(X > x), X ~ χ'²(df, λ). Poisson ağırlıklı merkezi χ² karışımı.
    Seri, Poisson kütlesinin tepesinden (k≈λ/2) iki yöne yayılarak toplanır;
    büyük λ'da alt taşmayı önler."""
    if lam == 0:
        return float(gammaincc(df / 2.0, x / 2.0))
    h = lam / 2.0
    k0 = int(h)
    logw0 = -h + k0 * math.log(h) - math.lgamma(k0 + 1) if h > 0 else 0.0
    total = 0.0
    # yukarı
    k, logw = k0, logw0
    while True:
        term = math.exp(logw) * gammaincc(df / 2.0 + k, x / 2.0)
        total += term
        if math.exp(logw) < tol and k > k0 + 10:
            break
        k += 1
        logw += math.log(h) - math.log(k)
    # aşağı
    k, logw = k0, logw0
    while k > 0:
        logw += math.log(k) - math.log(h)
        k -= 1
        term = math.exp(logw) * gammaincc(df / 2.0 + k, x / 2.0)
        total += term
        if math.exp(logw) < tol and k < k0 - 10:
            break
    return min(1.0, total)


def power_cont(w: float, n: float, alpha: float, df: int) -> float:
    c = float(chi2.isf(alpha, df))
    return ncx2_sf_series(c, df, n * w * w)


def n_fractional(w: float, alpha: float, power: float, df: int) -> float:
    """Sürekli N (pwr tarzı). Bisection; güç N'de monoton."""
    lo, hi = 1e-9, 2.0
    while power_cont(w, hi, alpha, df) < power:
        lo, hi = hi, hi * 2
        if hi > 1e9:
            return math.inf
    for _ in range(200):
        mid = (lo + hi) / 2
        if power_cont(w, mid, alpha, df) < power:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-10:
            break
    return hi


def statsmodels_n(w: float, alpha: float, power: float, df: int):
    try:
        from statsmodels.stats.power import GofChisquarePower
    except Exception:
        return None
    return float(GofChisquarePower().solve_power(effect_size=w, nobs=None, alpha=alpha,
                                                 power=power, n_bins=df + 1))
