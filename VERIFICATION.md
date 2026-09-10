# Verification record and reproduction

## Revision scope

The original ideal-ensemble theorem, its two original numerical implementations, and their baseline reports are unchanged. A [separate research supplement](FOLLOWUP_RESEARCH_NOTE.md) now adds a larger sparse domain, a transfer bound for the inspected sampling rule under independent random words, fixed-context and all-tag random-oracle corollaries, and a deterministic limitation of unrestricted aggregation.

These are different, explicitly stated scopes. The original and enlarged ideal-ensemble probabilities are over the choice of H. The random-oracle probabilities are over the sampled ideal oracle. None is a per-encryption error rate or a production security level. The all-tag bound below 2^-98 is not a revision of the original below-2^-162 bound: it concerns the larger event that some tag among all 2^64 tags fails, with every other generator input fixed.

## Checks performed

The primary source file was matched to its published Git blob identity before execution. In the preceding verification, its freshly generated JSON matched the published baseline in all fields. Both original scripts were rerun successfully for this supplement. The second report matched its previous baseline. The revised follow-up checker was executed twice, and the two generated reports matched in all fields.

| Check | Outcome |
|---|---|
| Original primary exact-arithmetic certificate | Passed |
| Original second implementation | Passed; generated report matched its earlier baseline |
| Original support-size coverage | All 128 even sizes from 2 through 256 |
| Follow-up support-size coverage | All 300 even sizes from 2 through 600 |
| Follow-up exact two-column contribution | Below 2^-163 |
| Six follow-up interval contributions | Each below 2^-200 |
| Enlarged-domain total bound | Below 2^-162 |
| Sampling-rule likelihood-ratio bound | At most 137438953472/137438953279, below 1 + 2^-29 |
| IID-word sampler transfer | Below 2^-162 |
| Fixed-context ideal-oracle bound, including finite-counter exceptional runs | Below 2^-162 |
| All-64-bit-tag ideal-oracle union bound | Below 2^-98 |
| Toy threshold enumeration | 38 reduced word/domain configurations passed |
| Toy duplicate-rejection checks | 2040 ordered distinct sequences passed |
| Artificial aggregation example | Equal syndromes for distinct aggregate witnesses, with the specified base weights |

Every inequality deciding pass/fail uses integers or rational arithmetic. Diagnostic decimal probabilities and logarithms are not certificates. The toy sampler and artificial-column checks illustrate the arguments; they do not replace universal symbolic proofs or execute Octra's C++ implementation. The all-tag calculation does not enumerate 2^64 matrices.

## Source identities

Git blob identities of the executed scripts:

```text
sparse_syndrome_checker.py  d748f8d95d0dec42700cd3344e791eb9340f4578
independent_recheck.py     5bfb84dbb39791c1fb4361333cda4670f88e3e69
followup_checker.py        8f78f8e3b2ed1ccfff3bcf0b407d17782d260cec
```

The primary checker and its baseline are unchanged from the initial publication. The second implementation reads the primary file to verify its identity, but does not import or execute its mathematical functions. Different line endings intentionally fail that byte-identity check.

The follow-up code and generated report were matched to the Git blob identities returned during publication. The report's blob identity is `7bea1a69da3bcc86c3ee8019d030b7f7ebfa7260`. Blob identity establishes which bytes were checked; it is not a mathematical or cryptographic endorsement.

## Reproduce

Use Python 3.9 or newer, standard library only. From the repository directory:

```sh
python sparse_syndrome_checker.py --output primary_results.local.json
python independent_recheck.py
python followup_checker.py --output followup_results.local.json
```

Run with assertions enabled: no `-O`/`-OO` flags and no `PYTHONOPTIMIZE`. The primary checker uses assertions. The other two use explicit exceptions for failed checks. The second command writes `independent_recheck_results.json` beside the script; the other commands keep the committed baselines untouched.

Compare the generated reports with [check_results.json](check_results.json), [independent_recheck_results.json](independent_recheck_results.json), and [followup_results.json](followup_results.json). Diagnostic floating-point last digits can vary between environments and are not used to decide the bounds. The artificial-column example uses Python's seeded sampling for reproducibility within the tested environment; its particular weights are illustrative, while the equality and domain checks are exact.

## What remains unverified

All implementations were produced within the same AI-assisted work. The primary and follow-up share the measure-domination and Chernoff approach; the second original implementation uses a different calculation of the numerical bounds but shares model assumptions. Their agreement is computational replication, **not independent peer review**, a formal proof-assistant result, or evidence of scientific novelty.

The checks do not establish that actual SHA-256 behaves as an ideal oracle, certify a concrete generated matrix, prove inversion hardness, tie witnesses to value-bearing ciphertext data, or establish HFHE confidentiality. The aggregation construction does not produce salt preimages, valid full ciphertexts, or an accepted network exploit.

The all-tag result applies only to one fixed parameter family in the ideal-oracle model. It concerns the property of each matrix separately, not injectivity across distinct tags or security of other protocol components.

See [the original derivation](technical_note.md), especially Sections 4.3 and 4.4, and [the follow-up derivations](FOLLOWUP_RESEARCH_NOTE.md), especially Sections 2 through 5, for the reasoning connecting numerical inequalities to the respective claims.
