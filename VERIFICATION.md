# Verification record and reproduction

## Revision scope

This revision expands the proof presentation and publishes a second numerical implementation. It does not change the ideal ensemble, the admissible domain, or the `2^-162` bound. In particular, it does not turn a model-level theorem into a statement about the actual Octra generator or deployed HFHE.

The probability is over selection of **H** from the ideal ensemble. For a good H, every syndrome in the restricted image has exactly one admissible witness. It is not a per-encryption error rate.

## Checks performed

The primary source file was matched to its published Git blob identity before execution. Its freshly generated JSON matched the published baseline in all fields. The second implementation was also executed successfully; its published JSON is the generated output, not a manually assumed list of passing checks.

| Check | Outcome |
|---|---|
| Primary exact-arithmetic certificate | Passed |
| Fresh primary JSON versus published baseline | All fields matched |
| Second hypergeometric-recurrence calculation for column pairs | Passed: union bound below `2^-163` |
| Second fixed-rational exponential-moment bounds | Each of four group bounds below `2^-200` |
| Complete coverage of even support sizes 2 through 256 | All 128 sizes covered |
| Second total-bound calculation | Passed: below `2^-162` |

All inequalities determining pass/fail use exact integers or rational arithmetic. Approximate masses, density ratios, and logarithms in the second report are for orientation only. Last digits may vary between platforms and must not be used to decide a bound.

## Source identities

Git blob identities of the two executed scripts:

```text
sparse_syndrome_checker.py  d748f8d95d0dec42700cd3344e791eb9340f4578
independent_recheck.py     5bfb84dbb39791c1fb4361333cda4670f88e3e69
```

The primary checker and its baseline results are unchanged from the initial publication. The second script reads the primary file to verify this identity, but neither imports nor executes its mathematical functions. A different primary file or altered line endings will fail that identity check intentionally.

## Reproduce

Use Python 3.9 or newer, standard library only. From the repository directory:

```sh
python sparse_syndrome_checker.py --output primary_results.local.json
python independent_recheck.py
```

Run with assertions enabled: no `-O`/`-OO` flags and no `PYTHONOPTIMIZE`. The primary checker uses assertions; the second uses explicit exceptions for failed checks. The second command writes `independent_recheck_results.json` beside the script.

Compare the generated reports with [check_results.json](check_results.json) and [independent_recheck_results.json](independent_recheck_results.json). Compare exact booleans and parameters; diagnostic floating-point values are not the certificate.

## What remains unverified

Both implementations were developed within the same AI-assisted work. They share the ideal-model assumptions and the measure-domination argument. This is a second computational implementation, **not independent peer review** or a proof-assistant formalization.

The checks do not certify a concrete generated matrix, exact uniformity of the SHA-256-based sampler, syndrome-inversion hardness, binding to ciphertext values, unrestricted composition, or HFHE confidentiality. The derivation and model-to-code interpretation remain open to external mathematical and cryptographic review.

See [the full derivation](technical_note.md), especially Sections 4.3 and 4.4, for the arguments connecting the checked inequalities to the theorem.
