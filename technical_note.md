# Sparse-Syndrome Uniqueness for an Idealized Octra-Parameter Ensemble

**Date:** 10 September 2026  
**Public code snapshot:** `octra-labs/lite_node`, commit `9e7ee19`  
**Revision:** expanded derivation and a second numerical implementation; theorem and bound unchanged.  
**Status:** AI-assisted mathematical analysis, not independently peer-reviewed. The numerical inequalities have been checked using exact arithmetic. This is not a C++ audit, a Lean/Coq formalization, an IND-CPA reduction, or a security certification of a deployed network. No claim of scientific priority is made.

## 1. Statement and scope

Let H be a binary matrix with 8,192 rows and 16,384 columns. Choose its columns independently. For each column, choose weight 192 or 193 with equal probability, and choose its support uniformly conditional on that weight.

Then

```math
\Pr_H[\exists u:\ \operatorname{wt}(u)\in\{2,4,\ldots,256\},\
\operatorname{wt}(Hu)\leq258]<2^{-162}.
```

Consequently, with probability greater than `1 - 2^-162` over the choice of **H** from this ideal matrix ensemble, the map

```math
(x,e)\longmapsto Hx\oplus e
```

is injective simultaneously on all pairs satisfying `wt(x)=128` and `wt(e)<=129`.

The exceptional event is a property of the selected matrix, not a per-encryption failure probability. For a good H, **every syndrome in the image of this restricted domain has exactly one admissible witness**.

This is a statement about uniqueness of a restricted internal representation. It says nothing by itself about the difficulty of recovering that representation, the confidentiality of HFHE messages, security of SHA-256, uniqueness of the implementation's salt-to-witness mapping, or security after arbitrary ciphertext operations. The exponent 162 describes a conservative upper bound on an exceptional event in the ideal matrix ensemble. It is not a security-level claim for Octra.

## 2. Connection to the inspected public code

In `pvac/include/pvac/core/types.hpp`, the `Params` defaults are `m_bits=8192`, `n_bits=16384`, `h_col_wt=192`, `x_col_wt=128`, and `err_wt=128`. These are source-code defaults, not verified parameters of a particular deployment.

In `crypto/matrix.hpp`, `gen_H` creates columns of base weight or base weight plus one. `sigma_from_H` selects 128 distinct columns at the stated defaults, XORs them and adds noise of weight 128 or 129. Its inputs include public context and a `uint64_t` salt; the numerical edge weight and plaintext are not arguments to this function.

The ideal distribution in Section 1 must not be confused with the implementation. The code deterministically generates columns using SHA-256 and a sampling procedure from public context. Transferring the ensemble statement to the implementation requires a separate argument about the generator and sampler, or certification of an appropriate property for a particular matrix. This note does not assume without proof that the sampler is exactly uniform or that SHA-256 is a random oracle.

The theorem covers the larger error domain wt(e) <= 129, rather than only the two weights selected by the generator. Conditional on a good H, it applies to every admissible pair, including correlated choices of x and e. It does not require x and e to be sampled independently.

## 3. Deterministic uniqueness lemma

Assume H has no nonzero u of even weight from 2 through 256 with wt(Hu) <= 258. Suppose two admissible pairs satisfy

```math
Hx\oplus e=Hx'\oplus e'.
```

Then H(x XOR x') = e XOR e'. If x = x', necessarily e = e'. Otherwise set u = x XOR x'. Because x and x' both have exactly 128 ones, u has a positive even weight no larger than 256. Also,

```math
\operatorname{wt}(Hu)=\operatorname{wt}(e\oplus e')
\leq\operatorname{wt}(e)+\operatorname{wt}(e')\leq258.
```

This contradicts the assumption, proving injectivity.

The restriction to even weights is essential. A single column has weight 192 or 193 and would fail an indiscriminately stated lower-bound condition on every sparse nonzero u. But a weight-one u cannot be the difference of two selectors that each have weight 128.

## 4. Probability bound in the ideal ensemble

Write m = 8192, n = 16384 and b = 258. For a fixed subset S of s columns, where s is even and between 2 and 256, consider the event that their XOR has weight at most b. Apply a union bound over all such subsets. Independence between the events for different subsets is not needed.

### 4.1 Two columns: an exact hypergeometric tail

Let the columns have weights a,c in {192,193}. If their supports overlap in J positions, their XOR has weight a+c-2J. Thus a bad pair requires

```math
J\geq\lceil(a+c-258)/2\rceil.
```

Conditional on the first column and the two weights,

```math
\Pr[J=j]=\frac{\binom{a}{j}\binom{m-a}{c-j}}{\binom{m}{c}}.
```

Averaging the four weight combinations gives the exact probability

```math
p_2=\frac14\sum_{a,c\in\{192,193\}}
\sum_{j=\lceil(a+c-258)/2\rceil}^{\min(a,c)}
\frac{\binom{a}{j}\binom{m-a}{c-j}}{\binom{m}{c}}.
```

The checker computes this as a rational number and verifies

```math
\binom{n}{2}p_2<2^{-163}.
```

### 4.2 Larger subsets: domination by a Bernoulli-column model

Let Q be the distribution of a column with independent bits, each equal to one with probability

```math
q=\frac{192.5}{8192}=\frac{385}{16384}.
```

Let P be the intended ideal distribution: weight 192 or 193 with equal probability, and uniform support conditional on weight. For a column v of weight w in {192,193},

```math
\frac{P(v)}{Q(v)}
=\frac{1}{2\Pr[\operatorname{Bin}(m,q)=w]}<18.
```

The checker verifies the last inequality by checking that each of the two binomial masses is greater than 1/36. Off those weights, P(v) = 0. Therefore, for s independent columns and any event A, P(A) <= 18^s Q(A).

Under Q, the XOR of s columns has independent coordinates, each equal to one with probability

```math
r_s=\frac{1-(1-2q)^s}{2}
=\frac{1-(7807/8192)^s}{2}.
```

Consequently,

```math
\Pr_P[\operatorname{wt}(H1_S)\leq b]
\leq18^s\Pr[\operatorname{Bin}(m,r_s)\leq b].
```

### 4.3 Chernoff bound and exact certification

For r > b/m, applying Markov's inequality to exp(-tX) and minimizing over t > 0 yields

```math
\Pr[\operatorname{Bin}(m,r)\leq b]
\leq e^{-mD(b/m\Vert r)}
=\left(\frac{mr}{b}\right)^b
\left(\frac{m(1-r)}{m-b}\right)^{m-b}.
```

For rational r, the last expression is rational. Its value can be compared to the target without floating-point logarithms or rounding.

For completeness, write the displayed bound as C(r). The optimizing exponential parameter is

```math
z_* = e^{-t_*} = \frac{b(1-r)}{r(m-b)} \in (0,1).
```

For X distributed as Bin(m,r), the event X <= b implies z^X >= z^b for 0 < z < 1. Markov's inequality gives

```math
\Pr[X\leq b]\leq z^{-b}(1-r+rz)^m.
```

Substituting z_* gives C(r) above. Its logarithmic derivative is

```math
\frac{d}{dr}\log C(r)=\frac{b-mr}{r(1-r)}<0
\qquad (r>b/m).
```

Thus replacing r_s by a smaller lower bound above b/m is conservative. Also r_s increases with s, since 0 < 7807/8192 < 1. For the counting factor A_s = binomial(n,s) * 18^s,

```math
\frac{A_{s+1}}{A_s}=18\frac{n-s}{s+1}>1
\qquad (0\leq s<256).
```

These two monotonicities justify using the smallest r and the largest counting factor in each interval. Divide the even support sizes into four groups:

| Even support sizes | Number of sizes | Strict lower bound for r_s | Bound on the entire group's contribution |
|---|---:|---:|---:|
| 4 | 1 | 7/80 | < 2^-200 |
| 6 through 16 | 6 | 1/8 | < 2^-200 |
| 18 through 64 | 24 | 1/4 | < 2^-200 |
| 66 through 256 | 96 | 7/16 | < 2^-200 |

For each group [s_min,s_max], the checker verifies, exactly,

```math
N_{\rm group}\binom{n}{s_{\max}}18^{s_{\max}}
\left(\frac{mr_{\min}}{b}\right)^b
\left(\frac{m(1-r_{\min})}{m-b}\right)^{m-b}<2^{-200}.
```

It also checks the lower bound for r_s at the group's smallest support size using integer arithmetic. Combining all contributions,

```math
\Pr[H\text{ is bad}]<2^{-163}+4\cdot2^{-200}<2^{-162}.
```

There are 1 + 6 + 24 + 96 = 127 larger even support sizes; including the two-column case covers all 128 possibilities from 2 through 256, without gaps. The union bound does not assume independence of different subsets' bad events.

Together with Section 3, this establishes the stated result within the ideal model, subject to review of the mathematical argument.

### 4.4 A second exact-arithmetic implementation

The companion `independent_recheck.py` does not call or import the primary checker's mathematical functions. It reuses the same ideal ensemble and the same pointwise domination argument, so it is not an independent validation of those assumptions. Both implementations were developed in the same AI-assisted work, not by independent peer reviewers.

For pairs, it starts at J = 0 and advances the hypergeometric mass by

```math
\frac{\Pr[J=j+1]}{\Pr[J=j]}
=\frac{(a-j)(c-j)}{(j+1)(m-a-c+j+1)}.
```

It adds every mass with a+c-2j <= b. For larger supports, it uses fixed rational z instead of optimizing the moment bound, and sums the combinatorial factors over all sizes in the group:

```math
U_{\rm group}^{(2)}
=z^{-b}(1-r_{\min}+r_{\min}z)^m
\sum_{\substack{s=s_{\min}\\s\ \mathrm{even}}}^{s_{\max}}
\binom ns 18^s.
```

Since 0 < z < 1, this moment expression decreases as r increases, so substituting r_min < r_s gives an upper bound. The second implementation checks r_s > r_min for **each** support size, and separately checks complete coverage of 2,4,...,256.

| Even support sizes | r_min | Fixed z | Exact group check |
|---|---:|---:|---:|
| 4 | 7/80 | 1/2 | < 2^-200 |
| 6 through 16 | 1/8 | 1/2 | < 2^-200 |
| 18 through 64 | 1/4 | 1/2 | < 2^-200 |
| 66 through 256 | 7/16 | 1/8 | < 2^-200 |

The separately evaluated two-column union bound is below 2^-163, and the sum of it and these four group bounds is below 2^-162. See [the generated second-run report](independent_recheck_results.json).

All inequalities deciding pass/fail use integers or `Fraction`. Floating-point values in the second report are diagnostic approximations only. The script also reads the primary file's bytes to check its Git blob identity; it does not execute that file.

## 5. Exact XOR composition

For any binary matrix H, whether or not it is random,

```math
(Hx_1\oplus e_1)\oplus(Hx_2\oplus e_2)
=H(x_1\oplus x_2)\oplus(e_1\oplus e_2).
```

Two syndromes can therefore be combined into a syndrome for the XOR of their witnesses without knowledge of those witnesses. The inspected ciphertext-compaction code XORs syndrome fields.

This property belongs to binary linear maps generally; it is not unique to hypergraphs. Neither a performance advantage nor the necessity of a particular representation has been established here.

The base uniqueness theorem cannot automatically be applied after composition. The new selector need not have weight 128, and the new error can exceed weight 129. XOR also does not preserve a full multiset history: identical terms cancel in pairs. A compositional analysis requires its own domain and bounds.

## 6. Representation is not confidentiality or semantic binding

The injectivity result concerns x and e, not the numerical ciphertext weight or plaintext. Using it for semantic binding would require an explicitly defined and verified relation between those values and the syndrome witness. This note does not establish that relation.

Uniqueness also does not imply inversion hardness. Even the identity function is injective. No reduction to LPN, syndrome-decoding hardness estimate, or security proof for the full adversarial view is provided here.

At fixed public context, a 64-bit salt gives the generator at most 2^64 salt inputs. A large matrix does not increase that input domain. This is not a statement that HFHE messages or keys have only 64 bits of security. Nor does injectivity of the witness-to-syndrome map imply injectivity of the preceding salt-to-witness map.

A fixed public permutation of syndrome coordinates preserves equality and inequality, so it preserves this injectivity property. It does not introduce a new secret.

## 7. An algebraic limitation: XOR versus odd-characteristic addition

For odd p, there is no nonzero map T from F_p to a binary vector space, depending only on the field value, that satisfies

```math
T(a+b)=T(a)\oplus T(b)
```

for all a,b. Given any v, choose a = v/2. Then T(v) = T(a+a) = T(a) XOR T(a) = 0.

Thus a nontrivial, deterministic and fully additive binary tag of the field value alone cannot have this form. This does not rule out randomized commitments, computation-history tags, additional metadata, separate proof systems, or restricted domains. These are different constructions and need separate definitions and analysis.

## 8. Reproduction and verification status

Use Python 3.9 or newer, with its standard library only. From the repository directory run:

```sh
python sparse_syndrome_checker.py --output primary_results.local.json
python independent_recheck.py
```

The first command writes a fresh primary report without overwriting the committed baseline. The second writes `independent_recheck_results.json` next to its script. Run without `-O`/`-OO` or `PYTHONOPTIMIZE`, because the original primary checker uses assertions. The second implementation uses explicit exceptions for its checks.

The [primary baseline](check_results.json) records the Section 4.1-4.3 checks. The [second-run baseline](independent_recheck_results.json) records Section 4.4 checks. A fresh primary run was compared field-for-field against the published baseline and matched. Both implementations were rerun successfully for this revision. [VERIFICATION.md](VERIFICATION.md) records identities and verification scope.

This is not Monte Carlo and not a proof-assistant formalization. The programs verify finite numerical inequalities; they do not certify the whole argument or its correspondence to the C++ implementation. Neither certifies a concrete generated H, proves inversion hardness, or audits HFHE.

The two implementations share assumptions and were produced within the same AI-assisted analysis. Their agreement is a useful computational cross-check, not independent expert review. The mathematical argument remains open to external review and correction.

## 9. Conclusion

The result establishes a narrowly scoped positive property of an ideal sparse binary encoding at parameters drawn from a public Octra snapshot: with high probability over matrix selection, every syndrome in the restricted image has a unique admissible sparse witness.

It does not establish a new general cryptographic primitive, a necessary role for hypergraphs, a production security level, or full HFHE confidentiality. The main next questions concern the actual matrix generator, the relationship to ciphertext semantics, and preservation of relevant properties under composition.

## Public code references

[Parameter defaults](https://github.com/octra-labs/lite_node/blob/9e7ee19/pvac/include/pvac/core/types.hpp) · [Matrix and syndrome generator](https://github.com/octra-labs/lite_node/blob/9e7ee19/pvac/include/pvac/crypto/matrix.hpp) · [Encryption and compaction](https://github.com/octra-labs/lite_node/blob/9e7ee19/pvac/include/pvac/ops/encrypt.hpp)

The mathematical argument uses standard tools: linearity, hypergeometric probabilities, domination of probability measures, Chernoff bounds and the union bound. The particular numerical bound is part of this unreviewed analysis, not a theorem attributed to the source-code authors.
