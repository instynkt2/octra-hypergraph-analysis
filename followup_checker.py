#!/usr/bin/env python3
"""Numerical certificates for the public follow-up research supplement.

Models only: not an Octra C++ execution, actual-SHA-256 proof, deployed-network
check, or a proof of HFHE confidentiality. Symbolic derivations are in the
companion note. Uses exact arithmetic for every pass/fail decision. Toy tests
are sanity checks, not universal proofs. Standard library; Python 3.9+.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
from itertools import permutations
import json
from math import comb, log2
from pathlib import Path
from random import Random

M, N, BASE_COLUMN_WEIGHT, ERROR_LIMIT = 8192, 16384, 192, 129
B = 2 * ERROR_LIMIT
WORD_SPACE = 1 << 64


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArithmeticError(message)


def log2_fraction(v: F) -> float:
    """Diagnostic only: never used for a proof comparison."""
    return log2(v.numerator) - log2(v.denominator)


def exact_pair_bound() -> F:
    probability = F(0)
    for a in (192, 193):
        for c in (192, 193):
            j_min = (a + c - B + 1) // 2
            numerator = sum(comb(a, j) * comb(M - a, c - j)
                            for j in range(j_min, min(a, c) + 1))
            probability += F(numerator, comb(M, c)) / 4
    return comb(N, 2) * probability


def ensemble_extension() -> tuple[dict, F]:
    q = F(385, 16384)
    for weight in (192, 193):
        mass = comb(M, weight) * q**weight * (1 - q)**(M - weight)
        require(mass > F(1, 36), 'column domination failed')
    pair = exact_pair_bound()
    require(pair < F(1, 1 << 163), 'pair bound failed')
    groups = [(4, 4, F(7, 80)), (6, 16, F(1, 8)),
              (18, 64, F(1, 4)), (66, 256, F(7, 16)),
              (258, 512, F(511, 1024)), (514, 600, F(511, 1024))]
    covered = [2]
    total = pair
    rows = []
    for lo, hi, r in groups:
        support_sizes = list(range(lo, hi + 1, 2))
        covered.extend(support_sizes)
        require(F(B, M) < r < F(1, 2), 'invalid lower-tail parameter')
        for s in support_sizes:
            rs = (1 - (1 - 2*q)**s) / 2
            require(rs > r, 'r lower bound failed')
        for s in range(lo, hi):
            require(18 * (N - s) > s + 1, 'counting-factor monotonicity failed')
        chernoff = (F(M, B)*r)**B * (F(M, M-B)*(1-r))**(M-B)
        bound = len(support_sizes) * comb(N, hi) * 18**hi * chernoff
        require(bound < F(1, 1 << 200), 'group bound failed')
        total += bound
        rows.append({'lo': lo, 'hi': hi, 'even_sizes': len(support_sizes),
                     'r_lower_bound': str(r), 'exact_below_2_minus_200': True,
                     'log2_bound_diagnostic': log2_fraction(bound)})
    require(covered == list(range(2, 601, 2)), 'support coverage failed')
    require(total < F(1, 1 << 162), 'extended total bound failed')
    return ({'scope': 'Ideal independent mixed-weight columns',
             'even_difference_supports': '2,4,...,600',
             'number_of_support_sizes': len(covered),
             'corollary_domain': 'even wt(x) <= 300; wt(e) <= 129',
             'exact_pair_below_2_minus_163': True,
             'log2_pair_bound_diagnostic': log2_fraction(pair),
             'groups': rows, 'exact_total_below_2_minus_162': True}, total)


def sampler_transfer() -> dict:
    # IID uniform 64-bit words, not actual SHA-256. The listed C++ threshold
    # accepts [0, 2^64-M], including both endpoints, at power-of-two M.
    D = WORD_SPACE
    A = D - M + 1
    p0 = F(D // M, A)
    p_other = F(D // M - 1, A)
    require(p0 + (M - 1)*p_other == 1, 'probability normalization failed')
    require(p0 / p_other == F(D, D-M), 'density-ratio formula failed')
    L = N * 193
    alpha = F(L * M, D)
    require(alpha < 1, 'invalid Bernoulli inequality range')
    # Bernoulli's inequality gives (1-M/D)^(-L) <= 1/(1-L*M/D).
    factor_upper = 1 / (1 - alpha)
    require(factor_upper < 1 + F(1, 1 << 29), 'sampler factor bound failed')
    ideal_coarse = F(1, 1 << 163) + 6 * F(1, 1 << 200)
    require(factor_upper * ideal_coarse < F(1, 1 << 162), 'IID sampler transfer failed')

    # Fixed-context ideal random-oracle coupling: first 1024 raw words in
    # each column fit far below 64-bit counter rollover. Before obtaining
    # 193 distinct rows, a raw attempt fails with probability <1/32.
    raw_fail_upper = F(192, M) + F(M-1, D)
    require(raw_fail_upper < F(1, 32), 'raw attempt failure bound failed')
    raw_words = 1024
    minimum_failures = raw_words - (193 - 1)
    slow_column_bound = F(1 << raw_words) * F(1, 32)**minimum_failures
    slow_matrix_bound = N * slow_column_bound
    require(slow_column_bound == F(1, 1 << 3136), 'column exponent mismatch')
    require(slow_matrix_bound == F(1, 1 << 3122), 'matrix exponent mismatch')
    rom_bound = factor_upper * ideal_coarse + slow_matrix_bound
    require(rom_bound < F(1, 1 << 162), 'fixed-context ROM transfer failed')
    return {'scope': 'Exact sampler logic under IID words; conditional fixed-context ROM corollary',
            'word_bits': 64, 'row_domain': M, 'maximum_total_unique_picks': L,
            'p_zero': str(p0), 'p_other': str(p_other),
            'one_draw_total_variation': str(F(M-1, M*A)),
            'per_unique_pick_density_ratio_upper': str(F(D, D-M)),
            'whole_matrix_factor_rational_upper': str(factor_upper),
            'factor_minus_one_diagnostic': float(factor_upper-1),
            'exact_factor_below_one_plus_2_minus_29': True,
            'exact_transferred_bound_below_2_minus_162': True,
            'raw_word_cap_per_column_for_coupling': raw_words,
            'slow_matrix_probability_upper': '2^-3122',
            'exact_fixed_context_ROM_bound_below_2_minus_162': True,
            'actual_sha256_guarantee': False,
            'scope_of_this_result': 'One context fixed independently of the oracle; see context_family_union_bound for all tags'}


def context_family_union_bound() -> dict:
    """Union bound over every 64-bit canon_tag, only in the ideal-hash model.

    No tags or matrices are enumerated. This checks the arithmetic of the
    finite-family corollary, not the random-oracle modeling assumptions.
    Independence of different tags' bad events is not required.
    """
    L = N * 193
    factor_upper = 1 / (1 - F(L * M, WORD_SPACE))
    one_context_upper = factor_upper * (F(1, 1 << 163) + 6*F(1, 1 << 200)) + F(1, 1 << 3122)
    require(one_context_upper < F(1, 1 << 162), 'fixed-context premise failed')
    tag_count = 1 << 64
    all_tags_upper = tag_count * one_context_upper
    require(all_tags_upper < F(1, 1 << 98), 'all-tag union bound failed')
    require(162 - 64 == 98, 'exponent relation failed')
    return {
        'scope': 'One shared ideal random oracle; fixed defaults; all uint64 canon_tag values',
        'tag_count': str(tag_count),
        'single_context_bound_below_2_minus_162': True,
        'all_tags_bound_below_2_minus_98': True,
        'event': 'Some tag fails the extended sparse-distance condition or its modeled generation does not finish',
        'probability_over': 'The sampled ideal oracle, not tags, encryptions, or actual SHA-256',
        'adaptive_tag_selection_covered_in_this_model': True,
        'arbitrary_parameter_selection_covered': False,
        'cross_tag_syndrome_injectivity_claimed': False,
        'tags_or_matrices_enumerated': False,
        'actual_sha256_guarantee': False,
    }


def exhaustive_toy_sampler_checks() -> dict:
    """Enumerate smaller word spaces; actual 64-bit code is not executed."""
    threshold_cases = 0
    for bits in range(3, 11):
        D = 1 << bits
        for power in range(1, min(bits, 7)):
            domain = 1 << power
            limit = (D-1) - ((D-1) % domain)
            counts = [0]*domain
            for x in range(D):
                if x <= limit:
                    counts[x % domain] += 1
            require(counts == [D//domain] + [D//domain-1]*(domain-1),
                    'exhaustive toy threshold formula failed')
            threshold_cases += 1
    sequence_cases = 0
    for bits, domain, length in [(4, 4, 3), (5, 8, 3), (6, 8, 4)]:
        D = 1 << bits
        A = D - domain + 1
        p = [F(D//domain, A)] + [F(D//domain-1, A)]*(domain-1)
        c = F(D, D-domain)
        for sequence in permutations(range(domain), length):
            used_mass = F(0)
            actual, uniform = F(1), F(1)
            for t, value in enumerate(sequence):
                actual *= p[value] / (1-used_mass)
                uniform *= F(1, domain-t)
                used_mass += p[value]
            require(actual <= uniform * c**length, 'toy unique-pick domination failed')
            sequence_cases += 1
    return {'scope': 'Sanity checks only; not proofs for all word sizes',
            'threshold_cases_enumerated': threshold_cases,
            'ordered_distinct_sequences_enumerated': sequence_cases,
            'all_checks_passed': True}


def bitvector(support: set[int]) -> int:
    out = 0
    for j in support:
        out |= 1 << j
    return out


def errors_with_xor(target: set[int]) -> tuple[set[int], set[int]]:
    """For weight <=193, represent target as XOR of errors of weight 128/129."""
    positions = sorted(target)
    split = len(positions)//2
    left, right = set(positions[:split]), set(positions[split:])
    pad_needed = 128-len(left)
    padding = set()
    for j in range(M):
        if j not in target:
            padding.add(j)
            if len(padding) == pad_needed:
                break
    require(len(padding) == pad_needed, 'padding unavailable')
    a, b = left | padding, right | padding
    require(len(a) in (128,129) and len(b) in (128,129), 'base error weights invalid')
    require(a ^ b == target, 'error decomposition failed')
    return a,b


def aggregation_model_example() -> dict:
    # These are artificial columns, not an Octra hash-generated matrix.
    rng = Random(20260910)
    h_i = set(rng.sample(range(M), 192))
    h_j = set(rng.sample(range(M), 193))
    difference = h_i ^ h_j
    positions = sorted(difference)
    p = set(positions[:len(positions)//2])
    q = set(positions[len(positions)//2:])
    e1,e2 = errors_with_xor(p)
    e3,e4 = errors_with_xor(q)
    # A and B share 127 columns; differ in column indices 0 and 129.
    A = set(range(128))
    BB = (A - {0}) | {129}
    common = 0
    for _ in range(127):
        common ^= bitvector(set(rng.sample(range(M), 192)))
    HA, HB = common ^ bitvector(h_i), common ^ bitvector(h_j)
    left_syndrome = (HA ^ bitvector(e1)) ^ (HA ^ bitvector(e2))
    right_syndrome = (HA ^ bitvector(e3)) ^ (HB ^ bitvector(e4))
    require(left_syndrome == right_syndrome, 'aggregate equality failed')
    require((A ^ A) != (A ^ BB), 'aggregate selectors should differ')
    require(len(A) == len(BB) == 128, 'base selector weights invalid')
    return {'scope': 'Broad algebraic witness domain only; no salt preimages or accepted transactions',
            'all_base_selector_weights': [128,128,128,128],
            'all_base_error_weights': list(map(len,[e1,e2,e3,e4])),
            'two_column_difference_weight': len(difference),
            'left_aggregate_selector_weight': 0,
            'right_aggregate_selector_weight': 2,
            'left_aggregate_error_weight': len(p),
            'right_aggregate_error_weight': len(q),
            'aggregate_syndromes_equal': True,
            'aggregate_witnesses_distinct': True,
            'an_attack_on_deployed_HFHE': False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('followup_results.json'))
    args = parser.parse_args()
    ensemble, _ = ensemble_extension()
    out = {'status': 'Public AI-assisted research supplement; not independently peer-reviewed',
           'ensemble_extension': ensemble,
           'sampler_transfer': sampler_transfer(),
           'context_family_union_bound': context_family_union_bound(),
           'toy_sampler_checks': exhaustive_toy_sampler_checks(),
           'aggregation_example': aggregation_model_example(),
           'not_established': ['Actual-SHA-256 behavior or a particular generated matrix',
                               'Efficient decoding or syndrome-inversion hardness',
                               'Semantic binding to ciphertext values',
                               'Full HFHE security or protocol exploit',
                               'Scientific novelty or independent expert review']}
    text = json.dumps(out, indent=2) + '\n'
    args.output.write_text(text, encoding='utf-8')
    print(text)

if __name__ == '__main__':
    main()
