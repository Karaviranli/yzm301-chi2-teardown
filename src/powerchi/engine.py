"""Hesap motoru: χ² testi, olumsallık tablosu (contingency tables).

Bu modül projedeki TEK hesap katmanıdır. CLI, MCP sunucusu ve ajan yalnızca
buradaki fonksiyonları çağırır; hiçbiri kendi başına güç/N hesabı yapmaz.

Temiz oda notu: Bu kod yalnızca SPEC.md'den yazıldı. Decompile çıktısı içermez.

Model (SPEC.md §2):
    λ  = N · w²                              (noncentrality)
    χ²_c = χ²⁻¹(1 − α ; df)                  (merkezi χ² kritik değeri)
    güç = 1 − F_ncχ²(χ²_c ; df, λ)           (noncentral χ² kuyruğu)
    a priori N = güç(N) ≥ hedef olan EN KÜÇÜK tam sayı N  (yukarı yuvarlama)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Sequence

from scipy.stats import chi2 as _chi2
from scipy.stats import ncx2 as _ncx2

TEST_ID = "chi2-contingency"

# SPEC §3.4: N araması için alt sınır. G*Power'daki gerçek alt sınır
# REA/kâhin ile doğrulanmalı (LEDGER L-07). Değiştirmek için tek yer burası.
N_MIN = 1
N_MAX = 100_000_000  # bundan büyük N "ulaşılamaz" kabul edilir (SPEC §3.5)

DEFAULT_PRECISION = 4  # CLI sözleşmesindeki örnek çıktı 4 basamak kullanıyor


class InputError(ValueError):
    """Geçersiz girdi. CLI bunu {"error": ...} ve çıkış kodu 2'ye çevirir."""


# --------------------------------------------------------------------------
# Doğrulama
# --------------------------------------------------------------------------

def _finite(name: str, x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        raise InputError(f"{name} sayısal olmalı (verilen: {x!r})")
    if math.isnan(v) or math.isinf(v):
        raise InputError(f"{name} sonlu bir sayı olmalı (verilen: {x!r})")
    return v


def _check_alpha(alpha) -> float:
    a = _finite("alpha", alpha)
    if not (0.0 < a < 1.0):
        raise InputError(f"alpha 0 ile 1 arasında (uçlar hariç) olmalı (verilen: {a})")
    return a


def _check_df(df) -> int:
    d = _finite("df", df)
    if d != int(d):
        raise InputError(f"df tam sayı olmalı (verilen: {df})")
    d = int(d)
    if d < 1:
        raise InputError(f"df en az 1 olmalı (verilen: {d})")
    return d


def _check_w(w, *, allow_zero: bool) -> float:
    v = _finite("w", w)
    if v < 0:
        raise InputError(f"w negatif olamaz (verilen: {v})")
    if v == 0 and not allow_zero:
        raise InputError("w = 0 iken hiçbir N hedef güce ulaşamaz (a priori tanımsız)")
    return v


def _check_n(n) -> int:
    v = _finite("n", n)
    if v != int(v):
        raise InputError(f"n (toplam örneklem) tam sayı olmalı (verilen: {n})")
    v = int(v)
    if v < 1:
        raise InputError(f"n en az 1 olmalı (verilen: {v})")
    return v


# --------------------------------------------------------------------------
# Çekirdek dağılım hesapları
# --------------------------------------------------------------------------

def critical_chi2(alpha: float, df: int) -> float:
    """Merkezi χ² dağılımının üst α kantili."""
    return float(_chi2.isf(alpha, df))


def ncp(w: float, n: int) -> float:
    """Noncentrality λ = N·w². Kayan nokta artığını (7.919999…) temizlemek için
    w² önce hesaplanır, sonra 12 anlamlı basamağa yuvarlanır."""
    return float(f"{n * (w * w):.12g}")


def power_at(w: float, n: int, alpha: float, df: int) -> float:
    lam = ncp(w, n)
    crit = critical_chi2(alpha, df)
    if lam == 0.0:
        return float(_chi2.sf(crit, df))  # = alpha
    return float(_ncx2.sf(crit, df, lam))


# --------------------------------------------------------------------------
# Sonuç tipleri
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class APrioriResult:
    n_total: int
    actual_power: float
    critical: float
    df: int
    ncp: float

    def to_dict(self, precision: int = DEFAULT_PRECISION) -> dict:
        d = asdict(self)
        for k in ("actual_power", "critical", "ncp"):
            d[k] = round(d[k], precision)
        return d


@dataclass(frozen=True)
class PostHocResult:
    n_total: int
    power: float
    critical: float
    df: int
    ncp: float

    def to_dict(self, precision: int = DEFAULT_PRECISION) -> dict:
        d = asdict(self)
        for k in ("power", "critical", "ncp"):
            d[k] = round(d[k], precision)
        return d


# --------------------------------------------------------------------------
# Modlar
# --------------------------------------------------------------------------

def a_priori(w, alpha, power, df, *, n_min: int = N_MIN, n_max: int = N_MAX) -> APrioriResult:
    """Hedef güce ulaşan en küçük toplam N (SPEC §3).

    Çözücü: güç N'de monoton artan olduğundan önce üstel adımla bir üst sınır
    bulunur, ardından tam sayılar üzerinde ikili arama yapılır. Sonuç, kesirli
    N'nin tavanı ile aynıdır ama kesirli kökün kayan nokta hatasından etkilenmez.
    """
    w = _check_w(w, allow_zero=False)
    alpha = _check_alpha(alpha)
    target = _finite("power", power)
    if not (0.0 < target < 1.0):
        raise InputError(f"power 0 ile 1 arasında (uçlar hariç) olmalı (verilen: {target})")
    if target <= alpha:
        raise InputError(
            f"power ({target}) alpha'dan ({alpha}) büyük olmalı; aksi hâlde N=0 bile yeterlidir ve a priori tanımsızdır"
        )
    df = _check_df(df)

    def ok(n: int) -> bool:
        return power_at(w, n, alpha, df) >= target

    lo = n_min
    if ok(lo):
        n = lo
    else:
        hi = max(lo * 2, 2)
        while not ok(hi):
            lo = hi
            hi *= 2
            if hi > n_max:
                raise InputError(
                    f"hedef güç {n_max} denekle bile sağlanamıyor (w çok küçük olabilir)"
                )
        # değişmez: ok(lo) == False, ok(hi) == True
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid
        n = hi

    return APrioriResult(
        n_total=n,
        actual_power=power_at(w, n, alpha, df),
        critical=critical_chi2(alpha, df),
        df=df,
        ncp=ncp(w, n),
    )


def post_hoc(w, alpha, n, df) -> PostHocResult:
    w = _check_w(w, allow_zero=True)
    alpha = _check_alpha(alpha)
    n = _check_n(n)
    df = _check_df(df)
    return PostHocResult(
        n_total=n,
        power=power_at(w, n, alpha, df),
        critical=critical_chi2(alpha, df),
        df=df,
        ncp=ncp(w, n),
    )


# --------------------------------------------------------------------------
# Etki büyüklüğü (G*Power'daki "Determine" penceresinin karşılığı)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class EffectSizeResult:
    w: float
    df: int
    rows: int
    cols: int

    def to_dict(self, precision: int = DEFAULT_PRECISION) -> dict:
        d = asdict(self)
        d["w"] = round(d["w"], precision)
        return d


def w_from_table(table: Sequence[Sequence[float]]) -> EffectSizeResult:
    """H1 altındaki hücre olasılıklarından (ya da frekanslarından) Cohen w.

    H0 (bağımsızlık) hücreleri satır ve sütun marjinallerinin çarpımıdır:
        p0_ij = r_i · c_j
        w     = sqrt( Σ (p1_ij − p0_ij)² / p0_ij )
        df    = (satır − 1)(sütun − 1)
    Girdi olasılık değilse toplamına bölünerek normalize edilir.
    """
    if not table or not all(table):
        raise InputError("tablo boş olamaz")
    ncols = len(table[0])
    if any(len(r) != ncols for r in table):
        raise InputError("tablonun tüm satırları aynı sayıda hücre içermeli")
    nrows = len(table)
    if nrows < 2 or ncols < 2:
        raise InputError("olumsallık tablosu en az 2×2 olmalı")
    cells = [[_finite("hücre", x) for x in r] for r in table]
    if any(x < 0 for r in cells for x in r):
        raise InputError("hücre değerleri negatif olamaz")
    total = sum(sum(r) for r in cells)
    if total <= 0:
        raise InputError("hücrelerin toplamı sıfırdan büyük olmalı")
    p = [[x / total for x in r] for r in cells]
    rm = [sum(r) for r in p]
    cm = [sum(p[i][j] for i in range(nrows)) for j in range(ncols)]
    if any(v == 0 for v in rm) or any(v == 0 for v in cm):
        raise InputError("tamamen sıfır olan satır ya da sütun olamaz")
    s = 0.0
    for i in range(nrows):
        for j in range(ncols):
            p0 = rm[i] * cm[j]
            s += (p[i][j] - p0) ** 2 / p0
    return EffectSizeResult(w=math.sqrt(s), df=(nrows - 1) * (ncols - 1), rows=nrows, cols=ncols)


def w_from_rates(rates: Sequence[float], weights: Sequence[float] | None = None) -> EffectSizeResult:
    """Klinik kısayol: k grubun 'yanıt oranları' → k×2 tablo → w.

    rates   : her grubun yanıt (başarı) oranı, 0..1
    weights : grupların toplam örneklemdeki payı (verilmezse eşit)
    """
    if not rates or len(rates) < 2:
        raise InputError("en az iki grubun yanıt oranı gerekli")
    rs = [_finite("oran", r) for r in rates]
    if any(not (0.0 <= r <= 1.0) for r in rs):
        raise InputError("yanıt oranları 0 ile 1 arasında olmalı")
    if weights is None:
        ws = [1.0] * len(rs)
    else:
        if len(weights) != len(rs):
            raise InputError("weights uzunluğu rates ile aynı olmalı")
        ws = [_finite("ağırlık", x) for x in weights]
        if any(x <= 0 for x in ws):
            raise InputError("grup ağırlıkları pozitif olmalı")
    table = [[wt * r, wt * (1 - r)] for r, wt in zip(rs, ws)]
    return w_from_table(table)


# --------------------------------------------------------------------------
# Tek giriş noktası (CLI ve MCP bunu çağırır)
# --------------------------------------------------------------------------

def compute(mode: str, *, w=None, alpha=None, power=None, df=None, n=None,
            precision: int = DEFAULT_PRECISION) -> dict:
    mode = (mode or "").strip().lower().replace("_", "-")
    if mode in ("a-priori", "apriori"):
        _require(w=w, alpha=alpha, power=power, df=df)
        return a_priori(w, alpha, power, df).to_dict(precision)
    if mode in ("post-hoc", "posthoc"):
        _require(w=w, alpha=alpha, n=n, df=df)
        return post_hoc(w, alpha, n, df).to_dict(precision)
    raise InputError(f"bilinmeyen mod: {mode!r} (geçerli: a-priori, post-hoc)")


def _require(**kw):
    missing = [k for k, v in kw.items() if v is None]
    if missing:
        raise InputError("eksik parametre: " + ", ".join("--" + m for m in missing))
