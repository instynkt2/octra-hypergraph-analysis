#!/usr/bin/env python3
"""Exact-arithmetic checker for the idealized sparse-syndrome bound.

This does NOT audit Octra C++ and does NOT prove full HFHE security.
It checks the finite inequalities used in the accompanying derivation.
"""
from __future__ import annotations
from fractions import Fraction
from math import comb
import argparse
import json
from pathlib import Path

M = 8192
N = 16384
D = 192
K = 128
T = 129
B = 2 * T


def pair_probability() -> Fraction:
    """Exact hypergeometric tail, averaged over the four weight pairs."""
    result = Fraction(0)
    for da in (D, D + 1):
        for db in (D, D + 1):
            threshold = (da + db - B + 1) // 2
            numerator = sum(
                comb(da, j) * comb(M - da, db - j)
                for j in range(threshold, min(da, db) + 1)
            )
            result += Fraction(numerator, comb(M, db)) / 4
    return result


def dominance_checks() -> dict[str, bool]:
    """Check P(column)/Q(column)<18 for Q=Bernoulli(385/16384)^8192."""
    den = 2 * M
    num = 2 * D + 1
    out = {}
    for w in (D, D + 1):
        lhs = 36 * comb(M, w) * pow(num, w) * pow(den - num, M - w)
        rhs = pow(den, M)
        out[f"binomial_mass_{w}_greater_than_1_over_36"] = lhs > rhs
    return out


def r_lower_bound_check(s: int, r: Fraction) -> bool:
    """Check r_s=(1-(7807/8192)^s)/2 > r using exact integers."""
    den = pow(M, s)
    num = den - pow(M - (2 * D + 1), s)
    return num * r.denominator > 2 * r.numerator * den


def chernoff_bound(r: Fraction) -> Fraction:
    """Exact rational form of exp[-M D(B/M || r)]."""
    if not Fraction(B, M) < r < Fraction(1, 2):
        raise ValueError("invalid Chernoff-tail parameter")
    return (
        pow(Fraction(M, B) * r, B)
        * pow(Fraction(M, M - B) * (1 - r), M - B)
    )


def check_certificate() -> dict:
    dom = dominance_checks()
    assert all(dom.values())

    pair = comb(N, 2) * pair_probability()
    pair_ok = pair < Fraction(1, 1 << 163)
    assert pair_ok

    groups = [
        (4, 4, Fraction(7, 80)),
        (6, 16, Fraction(1, 8)),
        (18, 64, Fraction(1, 4)),
        (66, 256, Fraction(7, 16)),
    ]

    details = []
    total = pair
    for lo, hi, r in groups:
        count = (hi - lo) // 2 + 1
        r_ok = r_lower_bound_check(lo, r)
        assert r_ok
        ub = count * comb(N, hi) * pow(18, hi) * chernoff_bound(r)
        tail_ok = ub < Fraction(1, 1 << 200)
        assert tail_ok
        total += ub
        details.append(
            {
                "min_s": lo,
                "max_s": hi,
                "number_of_even_s": count,
                "r_lower_bound": str(r),
                "r_lower_bound_check_passed": r_ok,
                "group_contribution_below_2_to_minus_200": tail_ok,
            }
        )

    total_ok = total < Fraction(1, 1 << 162)
    assert total_ok

    return {
        "version": 1,
        "scope": "Ideal independent-column ensemble; not actual SHA-256 outputs or full HFHE",
        "parameters": {
            "rows": M,
            "columns": N,
            "column_weights": [D, D + 1],
            "selector_weight": K,
            "maximum_error_weight": T,
        },
        "method": "Exact integer/Fraction arithmetic; hypergeometric tail, measure domination, Chernoff and union bounds",
        "dominance_checks": dom,
        "s_2_contribution_below_2_to_minus_163": pair_ok,
        "groups": details,
        "total_bound_below_2_to_minus_162": total_ok,
        "not_established": [
            "Security of SHA-256 or the actual matrix generator",
            "The property for a particular generated matrix",
            "Hardness of syndrome inversion",
            "Binding of the syndrome to ciphertext weights or plaintext",
            "Uniqueness after unrestricted XOR aggregation",
            "IND-CPA security of the complete HFHE construction",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    out = check_certificate()
    text = json.dumps(out, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
