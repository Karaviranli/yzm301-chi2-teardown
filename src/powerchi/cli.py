"""İnce CLI katmanı. Hesap yapmaz; argümanları ayrıştırıp engine.compute'u çağırır.

Sözleşme (ödev yönergesi, "CLI SÖZLEŞMESİ"):
  * Başarıda stdout'a TEK satır JSON, çıkış kodu 0
  * Geçersiz girdide {"error":"<açıklama>"} ve sıfırdan farklı çıkış kodu

Örnekler:
  gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.8 --df 1
  -> {"n_total":88,"actual_power":0.8035,"critical":3.8415,"df":1,"ncp":7.92}

  gpower-clone --test chi2-contingency --mode post-hoc --w 0.3 --alpha 0.05 --n 88 --df 1
  -> {"n_total":88,"power":0.8035,"critical":3.8415,"df":1,"ncp":7.92}

  gpower-clone --test chi2-contingency --mode effect-size --rates 0.6,0.4
  -> {"w":0.2,"df":1,"rows":2,"cols":2}
"""

from __future__ import annotations

import argparse
import json
import sys

from . import engine

EXIT_OK = 0
EXIT_INPUT = 2      # geçersiz girdi
EXIT_INTERNAL = 3   # beklenmeyen hata

SUPPORTED_TESTS = (engine.TEST_ID,)
# Sözleşmede tanımlı ama bu takımın kapsamı dışında kalan aileler:
OTHER_FAMILIES = ("t2-indep", "t-paired", "anova-oneway", "multireg-r2")


class _Parser(argparse.ArgumentParser):
    """argparse hatalarını da JSON sözleşmesine uydurur."""

    def error(self, message):  # noqa: D401
        raise engine.InputError(f"argüman hatası: {message}")


def _num(s: str) -> str:
    # Türkçe ondalık virgülü kabul et: "0,3" -> "0.3" (tek virgül varsa)
    return s.replace(",", ".") if s.count(",") == 1 and "." not in s else s


def _parse_list(s: str) -> list[float]:
    try:
        return [float(x) for x in s.replace(";", ",").split(",") if x.strip()]
    except ValueError:
        raise engine.InputError(f"sayı listesi okunamadı: {s!r}")


def _parse_table(s: str) -> list[list[float]]:
    rows = [r for r in s.split(";") if r.strip()]
    try:
        return [[float(x) for x in r.split(",") if x.strip()] for r in rows]
    except ValueError:
        raise engine.InputError(f"tablo okunamadı: {s!r} (biçim: 'a,b;c,d')")


def build_parser() -> argparse.ArgumentParser:
    p = _Parser(prog="gpower-clone", add_help=True,
                description="χ² olumsallık tablosu için güç analizi (G*Power 3.1.9.7 davranışının temiz oda yeniden yazımı)")
    p.add_argument("--test", required=True)
    p.add_argument("--mode", required=True,
                   help="a-priori | post-hoc | effect-size")
    p.add_argument("--w", type=_num, help="Cohen w etki büyüklüğü")
    p.add_argument("--alpha", type=_num, help="I. tip hata olasılığı")
    p.add_argument("--power", type=_num, help="hedef güç (1-β), a priori")
    p.add_argument("--df", type=_num, help="serbestlik derecesi = (satır-1)(sütun-1)")
    p.add_argument("--n", "--n-total", "--N", dest="n", type=_num, help="toplam örneklem, post hoc")
    p.add_argument("--rates", help="effect-size: grup yanıt oranları, ör. 0.6,0.4")
    p.add_argument("--weights", help="effect-size: grup payları, ör. 1,2 (varsayılan eşit)")
    p.add_argument("--table", help="effect-size: H1 hücre olasılıkları, ör. '0.3,0.2;0.2,0.3'")
    p.add_argument("--precision", type=int, default=engine.DEFAULT_PRECISION,
                   help="çıktıdaki ondalık basamak (varsayılan 4)")
    # Diğer ailelerin ortak bayrağı; χ² için anlamsız olduğundan kabul edilip yok sayılır.
    p.add_argument("--tails", help=argparse.SUPPRESS)
    p.add_argument("--ratio", help=argparse.SUPPRESS)
    return p


def run(argv: list[str] | None = None) -> tuple[dict, int]:
    """(çıktı sözlüğü, çıkış kodu) döndürür. Testler bunu doğrudan çağırır."""
    try:
        args = build_parser().parse_args(argv)
        test = args.test.strip().lower()
        if test not in SUPPORTED_TESTS:
            if test in OTHER_FAMILIES:
                raise engine.InputError(f"'{test}' bu uygulamanın kapsamı dışında; desteklenen: {engine.TEST_ID}")
            raise engine.InputError(f"bilinmeyen test: {args.test!r}; desteklenen: {engine.TEST_ID}")
        mode = args.mode.strip().lower()
        if mode == "effect-size":
            if args.table:
                res = engine.w_from_table(_parse_table(args.table))
            elif args.rates:
                weights = _parse_list(args.weights) if args.weights else None
                res = engine.w_from_rates(_parse_list(args.rates), weights)
            else:
                raise engine.InputError("effect-size için --rates ya da --table gerekli")
            return res.to_dict(args.precision), EXIT_OK
        out = engine.compute(mode, w=args.w, alpha=args.alpha, power=args.power,
                             df=args.df, n=args.n, precision=args.precision)
        return out, EXIT_OK
    except engine.InputError as e:
        return {"error": str(e)}, EXIT_INPUT
    except SystemExit as e:  # --help
        raise e
    except Exception as e:  # pragma: no cover - savunma amaçlı
        return {"error": f"iç hata: {type(e).__name__}: {e}"}, EXIT_INTERNAL


def main(argv: list[str] | None = None) -> int:
    out, code = run(argv)
    sys.stdout.write(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
