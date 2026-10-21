"""Motor birim testleri. Her test SPEC.md'deki bir senaryoya bağlıdır (S-xx)."""

import math

import pytest

from powerchi import engine
from powerchi.engine import InputError


# S-01 belgelenmiş vektör [DOK]
def test_documented_vector_n88():
    r = engine.a_priori(0.3, 0.05, 0.80, 1)
    assert r.n_total == 88
    assert round(r.critical, 4) == 3.8415
    assert round(r.ncp, 4) == 7.92


# S-02 N, hedef güce ulaşan EN KÜÇÜK tam sayıdır (yukarı yuvarlama)
@pytest.mark.parametrize("w,a,p,df", [(0.3, 0.05, 0.8, 1), (0.1, 0.05, 0.95, 1), (0.3, 0.05, 0.95, 5),
                                      (0.25, 0.01, 0.9, 6), (0.7, 0.1, 0.8, 2)])
def test_minimal_n(w, a, p, df):
    r = engine.a_priori(w, a, p, df)
    assert r.actual_power >= p
    if r.n_total > engine.N_MIN:
        assert engine.power_at(w, r.n_total - 1, a, df) < p


# S-03 λ = N·w²
def test_ncp_formula():
    r = engine.post_hoc(0.25, 0.05, 160, 3)
    assert r.ncp == pytest.approx(160 * 0.0625)


# S-04 kritik değer merkezi χ²'nin üst α kantili
def test_critical_value():
    assert engine.critical_chi2(0.05, 1) == pytest.approx(3.841458820694124)
    assert engine.critical_chi2(0.05, 5) == pytest.approx(11.070497693516351)


# S-05 post hoc, a priori'nin tersidir
def test_post_hoc_inverts_a_priori():
    a = engine.a_priori(0.3, 0.05, 0.9, 2)
    b = engine.post_hoc(0.3, 0.05, a.n_total, 2)
    assert b.power == pytest.approx(a.actual_power)


# S-06 w = 0 post hoc'ta gücü α'ya eşitler
def test_post_hoc_w_zero_power_equals_alpha():
    assert engine.post_hoc(0, 0.05, 100, 1).power == pytest.approx(0.05)


# S-07 güç N ile monoton artar
def test_monotone_power():
    ps = [engine.power_at(0.2, n, 0.05, 3) for n in range(1, 400, 7)]
    assert all(x <= y for x, y in zip(ps, ps[1:]))


# S-08 alt sınır (N_MIN) — G*Power davranışı kâhinle doğrulanacak (LEDGER L-07)
def test_lower_bound_n():
    assert engine.a_priori(3, 0.05, 0.8, 1).n_total == engine.N_MIN


# S-09 df büyüdükçe aynı w için N artar
def test_df_increases_n():
    ns = [engine.a_priori(0.3, 0.05, 0.8, d).n_total for d in (1, 2, 4, 8)]
    assert ns == sorted(ns) and len(set(ns)) == 4


# S-10 güç = α hata değildir (SPEC §3.7, kâhin I01)
def test_power_equals_alpha_gives_n1():
    r = engine.a_priori(0.3, 0.05, 0.05, 1)
    assert r.n_total == 1
    assert round(r.actual_power, 7) == 0.0603726


# S-11 kesirli df en yakın tam sayıya yuvarlanır, .5 yukarı (SPEC §4b)
@pytest.mark.parametrize("df,dfk,n", [(0.6, 1, 88), (1.4, 1, 88), (1.5, 2, 108), (1.6, 2, 108), (2.5, 3, 122)])
def test_fractional_df_rounds_half_up(df, dfk, n):
    r = engine.a_priori(0.3, 0.05, 0.80, df)
    assert r.df == dfk and r.n_total == n
    assert engine.post_hoc(0.3, 0.05, 88, df).df == dfk


# S-12 post hoc kesirli N en yakın tam sayıya yuvarlanır (SPEC §4, kâhin P08)
def test_post_hoc_fractional_n_rounds_half_up():
    r = engine.post_hoc(0.3, 0.05, 50.5, 1)
    assert r.n_total == 51
    assert round(r.ncp, 4) == 4.59
    assert round(r.power, 7) == 0.5724114
    assert engine.post_hoc(0.3, 0.05, 50.4, 1).n_total == 50


def test_post_hoc_n_upper_bound():
    assert engine.post_hoc(0.3, 0.05, engine.N_MAX_POST_HOC, 1).n_total == engine.N_MAX_POST_HOC
    with pytest.raises(InputError, match="arasında"):
        engine.post_hoc(0.3, 0.05, engine.N_MAX_POST_HOC + 1, 1)


# Geçersiz girdiler (SPEC §6, §8 "Geçersiz girdi")
@pytest.mark.parametrize("kw,msg", [
    (dict(w=0.3, alpha=0.05, power=0.04, df=1), "alpha'dan"),
    (dict(w=0, alpha=0.05, power=0.8, df=1), "büyük olmalı"),
    (dict(w=1e-6, alpha=0.05, power=0.8, df=1), "büyük olmalı"),
    (dict(w=-0.1, alpha=0.05, power=0.8, df=1), "büyük olmalı"),
    (dict(w=0.3, alpha=0, power=0.8, df=1), "alpha"),
    (dict(w=0.3, alpha=1, power=0.8, df=1), "alpha"),
    (dict(w=0.3, alpha=0.05, power=1, df=1), "power"),
    (dict(w=0.3, alpha=0.05, power=0.8, df=0), "df"),
    (dict(w=0.3, alpha=0.05, power=0.8, df=0.4), "df"),
    (dict(w=float("nan"), alpha=0.05, power=0.8, df=1), "sonlu"),
    (dict(w="abc", alpha=0.05, power=0.8, df=1), "sayısal"),
])
def test_invalid_a_priori(kw, msg):
    with pytest.raises(InputError, match=msg):
        engine.a_priori(**kw)


@pytest.mark.parametrize("n", [0, 0.4, -5])
def test_invalid_post_hoc_n(n):
    with pytest.raises(InputError):
        engine.post_hoc(0.3, 0.05, n, 1)


def test_post_hoc_negative_w():
    with pytest.raises(InputError, match="negatif"):
        engine.post_hoc(-0.1, 0.05, 100, 1)


def test_unreachable_n():
    with pytest.raises(InputError, match="sağlanamıyor"):
        engine.a_priori(1e-5, 0.05, 0.99, 1)


# Etki büyüklüğü
def test_w_from_rates_equal_groups():
    r = engine.w_from_rates([0.6, 0.4])
    assert r.w == pytest.approx(0.2) and r.df == 1


def test_w_from_table_matches_rates():
    a = engine.w_from_table([[0.3, 0.2], [0.2, 0.3]])
    b = engine.w_from_rates([0.6, 0.4])
    assert a.w == pytest.approx(b.w)


def test_w_from_table_independent_is_zero():
    assert engine.w_from_table([[0.06, 0.14], [0.24, 0.56]]).w == pytest.approx(0, abs=1e-12)


def test_w_unequal_weights_differs():
    assert engine.w_from_rates([0.6, 0.4], [1, 2]).w != pytest.approx(0.2)


def test_w_three_groups_df():
    assert engine.w_from_rates([0.5, 0.6, 0.7]).df == 2


@pytest.mark.parametrize("t", [[[0.5, 0.5]], [[0.1, 0.2], [0.3]], [[0, 0], [0.5, 0.5]], [[-1, 1], [1, 1]]])
def test_w_invalid_tables(t):
    with pytest.raises(InputError):
        engine.w_from_table(t)


def test_rounding_output():
    d = engine.a_priori(0.3, 0.05, 0.8, 1).to_dict()
    assert d == {"n_total": 88, "actual_power": 0.8035, "critical": 3.8415, "df": 1, "ncp": 7.92}
