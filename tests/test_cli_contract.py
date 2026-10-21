"""CLI sözleşme testleri: kara kutu olarak alt süreçle çalıştırılır."""

import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(*args):
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    p = subprocess.run([sys.executable, "-m", "powerchi", *args], capture_output=True, text=True, env=env)
    lines = p.stdout.strip().splitlines()
    assert len(lines) == 1, f"tek satır JSON bekleniyordu: {p.stdout!r}"
    return json.loads(lines[0]), p.returncode


BASE = ["--test", "chi2-contingency"]


def test_a_priori_contract_shape():
    out, code = run(*BASE, "--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8", "--df", "1")
    assert code == 0
    assert list(out) == ["n_total", "actual_power", "critical", "df", "ncp"]
    assert out == {"n_total": 88, "actual_power": 0.8035, "critical": 3.8415, "df": 1, "ncp": 7.92}


def test_post_hoc_contract_shape():
    out, code = run(*BASE, "--mode", "post-hoc", "--w", "0.3", "--alpha", "0.05", "--n", "88", "--df", "1")
    assert code == 0
    assert list(out) == ["n_total", "power", "critical", "df", "ncp"]


def test_effect_size():
    out, code = run(*BASE, "--mode", "effect-size", "--rates", "0.6,0.4")
    assert code == 0 and out["w"] == 0.2 and out["df"] == 1


def test_turkish_decimal_comma():
    a, _ = run(*BASE, "--mode", "a-priori", "--w", "0,3", "--alpha", "0,05", "--power", "0,8", "--df", "1")
    assert a["n_total"] == 88


def test_tails_flag_is_ignored():
    out, code = run(*BASE, "--mode", "a-priori", "--tails", "2", "--w", "0.3", "--alpha", "0.05",
                    "--power", "0.8", "--df", "1")
    assert code == 0 and out["n_total"] == 88


# S-10 güç = α geçerli (SPEC §3.7)
def test_power_equals_alpha_is_valid():
    out, code = run(*BASE, "--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.05", "--df", "1",
                    "--precision", "7")
    assert code == 0 and out["n_total"] == 1 and out["actual_power"] == 0.0603726


# S-11 kesirli df motora iletilir ve yuvarlanır (SPEC §4b)
@pytest.mark.parametrize("df,dfk,n", [("0.6", 1, 88), ("1,5", 2, 108), ("2.5", 3, 122)])
def test_fractional_df_cli(df, dfk, n):
    out, code = run(*BASE, "--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8", "--df", df)
    assert code == 0 and out["df"] == dfk and out["n_total"] == n


# S-12 kesirli N motora iletilir ve yuvarlanır (SPEC §4)
def test_fractional_n_cli():
    out, code = run(*BASE, "--mode", "post-hoc", "--w", "0.3", "--alpha", "0.05", "--n", "50.5", "--df", "1",
                    "--precision", "7")
    assert code == 0
    assert out == {"n_total": 51, "power": 0.5724114, "critical": 3.8414588, "df": 1, "ncp": 4.59}


@pytest.mark.parametrize("args", [
    ["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.04", "--df", "1"],
    ["--mode", "a-priori", "--w", "0", "--alpha", "0.05", "--power", "0.8", "--df", "1"],
    ["--mode", "a-priori", "--w", "-0.1", "--alpha", "0.05", "--power", "0.8", "--df", "1"],
    ["--mode", "post-hoc", "--w", "-0.1", "--alpha", "0.05", "--n", "100", "--df", "1"],
    ["--mode", "a-priori", "--w", "0.3", "--alpha", "0", "--power", "0.8", "--df", "1"],
    ["--mode", "a-priori", "--w", "0.3", "--alpha", "1", "--power", "0.8", "--df", "1"],
    ["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "1", "--df", "1"],
    ["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8", "--df", "0"],
    ["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8", "--df", "0.4"],
    ["--mode", "post-hoc", "--w", "0.3", "--alpha", "0.05", "--n", "0.4", "--df", "1"],
    ["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--df", "1"],
    ["--mode", "a-priori", "--w", "x", "--alpha", "0.05", "--power", "0.8", "--df", "1"],
    ["--mode", "compromise", "--w", "0.3", "--alpha", "0.05", "--power", "0.8", "--df", "1"],
    ["--mode", "post-hoc", "--w", "0.3", "--alpha", "0.05", "--n", "0", "--df", "1"],
    ["--mode", "a-priori", "--w", "0.3", "--alpha", "0.05", "--power", "0.8", "--df", "1", "--bilinmeyen", "1"],
])
def test_invalid_input_contract(args):
    out, code = run(*BASE, *args)
    assert code != 0
    assert list(out) == ["error"] and isinstance(out["error"], str) and out["error"]


def test_unknown_test_family_any():
    out, code = run("--test", "bilinmeyen", "--mode", "a-priori")
    assert code != 0 and list(out) == ["error"]


def test_unknown_test_family():
    out, code = run("--test", "t2-indep", "--mode", "a-priori")
    assert code != 0 and "error" in out


def test_missing_test_flag():
    out, code = run("--mode", "a-priori")
    assert code != 0 and "error" in out
