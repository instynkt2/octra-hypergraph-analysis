# Beyond the Ideal Ensemble: Sampler Transfer, an Enlarged Sparse Domain, and Limits of Aggregation

**Status:** Public AI-assisted research supplement; not independently peer-reviewed. No scientific-priority claim.  
**Date:** 10 September 2026.  
**Public source snapshot:** `octra-labs/lite_node`, commit `9e7ee19af38ba020497566ac73c268f42b20b9a4`.  
**Preceding analysis:** `instynkt2/octra-hypergraph-analysis`, mathematical baseline in revision `0b5d6d021ca4c30158a24fb9f8a3cf9e4687b091`.

This note develops three follow-up results and an additional finite-context-family corollary. All numerical inequalities used as certificates were checked with exact integer or rational arithmetic. This is not an execution or audit of the Octra C++ implementation, a proof for actual SHA-256, a proof-assistant formalization, or a protocol-security certification. The symbolic arguments below need external mathematical review. In particular, computational checks do not themselves prove that the model describes the deployed system.

## Executive statement

1. The slight nonuniformity of the inspected rejection sampler can be bounded **multiplicatively**, including duplicate rejection. Under independent uniform source words, the probability of any matrix event increases by a factor of at most `137438953472/137438953279`, which is less than `1 + 2^-29`, compared with the independent uniform-support ensemble. This is a probability-ratio bound, not a distance between particular matrices.
2. The original sparse-distance estimate extends to all positive even difference weights through **600**, keeping the failure bound below `2^-162`. Consequently the syndrome map is injective simultaneously over all selectors of **even weight at most 300**, with error weight at most 129.
3. That does **not** extend to unrestricted aggregation of two base witnesses. A deterministic construction gives collisions between distinct aggregate witnesses, even with all four base selectors of weight 128 and all four base errors of weight 128 or 129. This is a statement about the broad algebraic witness domain, not about the smaller image of the salt generator or acceptance by the full protocol.

A separately stated random-oracle corollary accounts for the finite counter by a stopping-time estimate. Section 4.1 extends this to all 64-bit context tags simultaneously with a bound below `2^-98`, while keeping every other generator parameter fixed. Both statements remain results in an ideal-hash model, not results for SHA-256 as implemented. The number 98 is not an HFHE security level.

## 1. Setting and public-code correspondence

Set `m = 8192`, `n = 16384`, with column weights in `{192,193}`. Arithmetic for the syndrome map is over the binary field:

```math
F_H(x,e)=Hx\oplus e.
```

The inspected `Params` defaults use selector weight 128 and base error weight 128. In `crypto/matrix.hpp`, `mixed_weight` chooses base weight or base plus one, and `prg_choose_k` collects distinct indices. `gen_H` uses this mechanism for columns. `sigma_from_H` uses it to choose 128 columns and 128 or 129 error positions at these defaults.

The established ideal ensemble P chooses the column weights independently and fairly, and each support uniformly conditional on weight. For a fixed H, neither x nor e needs to be random for the stated injectivity property.

In contrast, the source generator is deterministic, using SHA-256 on domain-separated encodings of public parameters, the column index, a context tag, and counters. This note does not identify actual SHA-256 with independent random outputs.

## 2. A larger ideal-model domain

### Proposition 1: sparse-distance extension

In the ideal ensemble P,

```math
\Pr_H\left[\exists u:\ 0<\operatorname{wt}(u)\leq600,
\quad \operatorname{wt}(u)\equiv0\pmod2,
\quad \operatorname{wt}(Hu)\leq258\right]<2^{-162}.
```

### Proof

For a fixed pair of columns of weights a,c in `{192,193}`, their intersection J is hypergeometric. Their XOR has weight a+c-2J. Average the exact tail over the four weight pairs, then multiply by the number of pairs:

```math
U_2=\binom n2\frac14\sum_{a,c\in\{192,193\}}
\sum_{j=\lceil(a+c-258)/2\rceil}^{\min(a,c)}
\frac{\binom aj\binom{m-a}{c-j}}{\binom mc}<2^{-163}.
```

For larger supports use Q, the product Bernoulli-column distribution with bit probability `q = 385/16384`. For a supported column v of weight w,

```math
\frac{P(v)}{Q(v)}=\frac1{2\Pr[\operatorname{Bin}(m,q)=w]}<18.
```

The checker verifies both relevant binomial masses exceed `1/36`. Therefore every event on s columns has P-probability at most `18^s` times its Q-probability. Under Q the XOR weight is Bin(m,r_s), with

```math
r_s=\frac{1-(7807/8192)^s}{2}.
```

For b = 258 and r > b/m define the rational Chernoff bound

```math
C_b(r)=\left(\frac{mr}{b}\right)^b
\left(\frac{m(1-r)}{m-b}\right)^{m-b}.
```

Markov's inequality applied to `z^X`, `0 < z < 1`, gives `Pr[X <= b] <= z^-b (1-r+rz)^m`. Choosing `z = b(1-r)/(r(m-b))` gives C_b(r). Its logarithmic derivative is `(b-mr)/(r(1-r)) < 0`. Thus substituting a smaller r above b/m gives a valid upper bound.

Also r_s increases with s, and `A_s = binomial(n,s) 18^s` increases through s = 600, since `A_(s+1)/A_s = 18(n-s)/(s+1) > 1` in this range.

The following six intervals cover every even s from 4 through 600:

| Even s | Count | Strict lower bound r_min | Entire-interval bound |
|---|---:|---:|---:|
| 4 | 1 | 7/80 | < 2^-200 |
| 6 through 16 | 6 | 1/8 | < 2^-200 |
| 18 through 64 | 24 | 1/4 | < 2^-200 |
| 66 through 256 | 96 | 7/16 | < 2^-200 |
| 258 through 512 | 128 | 511/1024 | < 2^-200 |
| 514 through 600 | 44 | 511/1024 | < 2^-200 |

For each interval the checker verifies exactly:

```math
N_{\rm interval}\binom n{s_{\max}}18^{s_{\max}}C_b(r_{\min})<2^{-200}.
```

It verifies `r_s > r_min` for each listed s, not just endpoints. Including s = 2 gives all 300 positive even sizes through 600. A union bound, which does not require independence of the different subsets' events, gives

```math
\Pr_P[H\text{ fails}]<2^{-163}+6\cdot2^{-200}<2^{-162}.
```

### Corollary: injectivity on all even selectors of weight at most 300

Let

```math
\mathcal D=\{(x,e):\operatorname{wt}(x)\leq300,
\ \operatorname{wt}(x)\equiv0\pmod2,
\ \operatorname{wt}(e)\leq129\}.
```

For a matrix satisfying Proposition 1's sparse-distance property, F_H is injective on D. Indeed, a collision with x != x' would give `u=x XOR x'` with positive even weight at most 600 and `wt(Hu)=wt(e XOR e') <= 258`. This is excluded. If x=x', equality forces e=e'.

The result holds simultaneously across different even selector weights, not merely for one weight at a time. The parity restriction is essential. Allowing both parities would permit a one-column difference, which can be absorbed by two errors of weight at most 129 because a column has weight at most 193.

The value 300 is a convenient certified domain size, not an optimal threshold and not a claimed deployed parameter. Keeping the error bound at 129 is essential. This is not a guarantee for arbitrary computations.

## 3. Transfer through the inspected sampling rule

This section first analyzes a sampler driven by an unlimited independent stream of uniform 64-bit words and independent fair weight bits. It retains the actual threshold comparison and duplicate-elimination logic. SHA-256 itself is not used or certified in this probability model.

### 3.1 The one-word distribution

Let D = 2^64 and M = 8192, with M dividing D. The inspected code uses

```cpp
uint64_t lim = UINT64_MAX - (UINT64_MAX % M);
if (x <= lim) return x % M;
```

Here `lim = D-M`, so the accepted interval is `[0,D-M]`, including both endpoints. It contains A = D-M+1 values. Consequently

```math
p_0=\frac{D/M}{A},\qquad
p_j=\frac{D/M-1}{A}\quad(1\leq j<M).
```

These probabilities are not exactly uniform. Their ratio is

```math
\frac{p_{\max}}{p_{\min}}=\frac D{D-M}=:c.
```

The total-variation distance from a uniform row is `(M-1)/(M A)`. That additive quantity is not the tool used for the rare-event transfer below: an additive error can be much larger than the event probability being studied. The multiplicative ratio preserves the useful scale.

### 3.2 Duplicate rejection does not invalidate the bound

Suppose t distinct indices have been selected and let U be their set. The next previously unseen row j has probability

```math
\frac{p_j}{1-\sum_{i\in U}p_i}.
```

There are M-t unselected indices, and their total probability is at least `(M-t)p_min`. Therefore

```math
\frac{\Pr[\text{next unseen row}=j\mid U]}{1/(M-t)}
\leq\frac{p_{\max}}{p_{\min}}=c.
```

Multiplying over k distinct choices bounds the probability of each ordered k-tuple by c^k times uniform sampling without replacement. Summing over the k! orders gives the same bound for unordered supports.

For n independent columns of weight at most 193, the matrix-event likelihood ratio is therefore bounded by

```math
R=c^{193n}=(1-M/D)^{-L},\qquad L=193n=3162112.
```

The fair weight choices have the same law in both models and add no ratio factor.

Bernoulli's inequality implies `(1-a)^L >= 1-La` for a=M/D and L a < 1, yielding

```math
R\leq\frac1{1-LM/D}
=\frac{137438953472}{137438953279}
<1+2^{-29}.
```

The rational bound's excess above one is approximately `1.4042598215e-9`. This decimal is diagnostic only; comparisons use exact fractions.

### Proposition 2: iid-word sampler transfer

For any matrix event E, the sampler model just defined satisfies

```math
\Pr_{\rm sampler}[E]\leq R\Pr_P[E].
```

Combining with Proposition 1 and retaining its stronger pre-rounding bound gives

```math
\Pr_{\rm sampler}[H\text{ fails}]
<\frac{137438953472}{137438953279}
\left(2^{-163}+6\cdot2^{-200}\right)<2^{-162}.
```

This absorbs the threshold's nonuniformity and duplicate rejection. It does not assert that actual SHA-256 supplies an independent random stream.

## 4. A fixed-context random-oracle corollary

This is a further conditional model statement, not an assertion about the deployed generator.

Replace the SHA-256 calls involved in H generation by a single ideal random function with independent uniform 256-bit outputs on distinct inputs. Fix the default parameters and canon_tag independently of the sampled oracle, and assume the byte encodings and domain separation from the pinned source.

The weight selector uses label `pvac.H.weight`. Row selection uses `pvac.dom.h_gen`, a fixed encoding of parameters, column number, canon_tag, and a counter. These input families are disjoint. Within one H generation, the column number and counter distinguish row-selection inputs until counter rollover. Splitting independent 256-bit outputs into four 64-bit words gives the source model used above, until such repetition. Independent oracle outputs are allowed to coincide by chance; the argument requires distinct inputs, not collision-free outputs.

The 64-bit counter is finite. To avoid silently modeling it as infinite, couple the two generators only until the first 1024 raw 64-bit words in each column. That uses at most 256 counter values per column, well below rollover.

Before 193 rows have been accepted, at most 192 distinct rows have been used. For each fresh raw word, the probability of either rejection by the threshold or repetition of a used index is at most

```math
\frac{192}{8192}+\frac{8191}{2^{64}}<\frac1{32}.
```

Failure to finish a column within 1024 raw words requires at least 832 unsuccessful attempts. Even though attempts' success status is history-dependent, the conditional failure bound is valid for each prefix. A union bound over sets of 832 failed positions gives

```math
\Pr[\text{column unfinished after 1024 words}]
\leq 2^{1024}(1/32)^{832}=2^{-3136}.
```

A union bound over 2^14 columns gives `2^-3122`. On the complementary event all oracle inputs needed for row generation are distinct and the coupling is exact. Conservatively count every exceptional run as failure, including possible nontermination. Hence

```math
\Pr_{\rm RO}[H\text{ fails or generation does not finish}]
<\frac{137438953472}{137438953279}
\left(2^{-163}+6\cdot2^{-200}\right)+2^{-3122}
<2^{-162}.
```

This is a conditional formal-model route from uniform supports to the generator's sampling logic. By itself this fixed-context result does not quantify adversarial selection of context. Section 4.1 gives a separate finite-family extension. Neither result establishes the property for actual SHA-256 or certifies one concrete matrix. In the present result the probability is over the oracle and the context is fixed independently. The entire C++ program, its hash implementation, memory behavior, and surrounding protocol have not been audited.

### 4.1 All 64-bit context tags under one ideal oracle

In `gen_H`, the varying context is `pk.canon_tag`. With all other inputs fixed to the specified defaults, this is a family of at most `2^64` matrix generators. The argument concerns this exact finite family, not freely variable dimensions or sampling rules.

Let O be one shared ideal random oracle and let B_t be the event that, at tag t, the modeled generator either produces a matrix failing Proposition 1's extended distance condition or fails to finish. The fixed-context argument applies separately to each constant t, so

```math
\Pr_O[B_t]<\varepsilon_0,
\qquad
\varepsilon_0=
\frac{137438953472}{137438953279}
\left(2^{-163}+6\cdot2^{-200}\right)+2^{-3122}
<2^{-162}.
```

Now union-bound over the entire tag domain:

```math
\Pr_O\left[\exists t\in\{0,1\}^{64}:B_t\right]
\leq\sum_{t\in\{0,1\}^{64}}\Pr_O[B_t]
<2^{64}\varepsilon_0<2^{-98}.
```

The events for different tags need not be independent. On the complementary event, every modeled tag generation succeeds and each resulting matrix separately has the extended injectivity property. Consequently selecting a tag adaptively, after inspecting the oracle, cannot violate that property on the complementary event. This is stronger than applying a fixed-context theorem to an oracle-dependent tag, which would not be justified by itself.

The statement remains narrow. The probability is over the ideal oracle. It is not a probability bound for actual deterministic SHA-256, an encryption failure rate, a measure of search work, or 98-bit HFHE security. It does not assert injectivity across different matrices/tags, nor does it cover changing other parameters. Other protocol components may have different security properties. A predeclared finite family of T such contexts similarly gives T times the per-context bound; replacing T by the number of adaptively tried contexts without further analysis is not asserted here.

The checker verifies the exact rational inequality `2^64 * epsilon_0 < 2^-98`. It does not generate, enumerate, or inspect all `2^64` matrices. This corollary is an elementary consequence of the previous conditional model result; no claim of a new general technique is made.

## 5. Why unrestricted two-way aggregation cannot inherit injectivity

The new selector-domain bound does not allow the error bound to grow freely. Here is a deterministic obstruction in the broad algebraic witness domain, valid for any H with enough columns and each column of weight at most 193.

Choose two distinct column indices i,j. Write

```math
v=H_i\oplus H_j,\qquad \operatorname{wt}(v)\leq386.
```

Split v into two disjoint supported vectors p,q, each of weight at most 193, so v=p XOR q. Any such vector z can be written as the XOR of two vectors with weights 128 or 129. To see this, partition its support into Z_1,Z_2 of sizes floor(wt(z)/2) and ceil(wt(z)/2), and choose a common padding set T outside the support with `128-floor(wt(z)/2)` elements. The two vectors supported on `Z_1 union T` and `Z_2 union T` have the required weights, and their XOR is z.

Thus find e_1,e_2,e_3,e_4, each of weight 128 or 129, such that

```math
e_1\oplus e_2=p,\qquad e_3\oplus e_4=q.
```

Choose selectors A,B of weight 128 which share 127 positions and satisfy `A XOR B = unit_i XOR unit_j`. Then

```math
F_H(A,e_1)\oplus F_H(A,e_2)=p
```

while

```math
F_H(A,e_3)\oplus F_H(B,e_4)
=H(A\oplus B)\oplus q=v\oplus q=p.
```

The aggregate witnesses are `(0,p)` and `(unit_i XOR unit_j,q)`, so they are distinct, but their syndromes are equal. All four base selectors have weight 128; all four base errors have weight 128 or 129.

This is not merely loss of ordering or duplication history: even the resulting aggregate witness pairs can differ. It is also not a contradiction to Proposition 1. For a good H, the two-column difference exceeds 258, so at least one aggregate error in this construction exceeds 129.

**Scope warning:** This construction chooses witnesses freely in the broad algebraic domain. It does not find salt preimages for them, produce valid full ciphertexts, satisfy the surrounding proof system, or demonstrate acceptance by a network. Those additional constraints can matter. The result only rules out deducing unrestricted aggregate-witness injectivity from the base theorem without further restrictions or mechanisms.

The checker includes one reproducible artificial-column example. It is not generated by Octra's SHA-256 code and is not a network test. The symbolic construction above, not that example, provides the universal argument.

## 6. What these results do and do not advance

The sampler-transfer bound addresses a specific gap between uniform subset sampling and the inspected threshold/duplicate logic. The stronger selector-domain bound extends a combinatorial property; it does not provide efficient decoding. The aggregation obstruction helps define which stronger statements cannot follow automatically.

The larger remaining questions are unchanged: how the actual hash-generated matrix behaves, whether witness recovery is hard, which verified relation ties witnesses to value-bearing ciphertext data, and which guarantees survive the operations accepted by the full protocol. No claim of an HFHE security proof, exploit, new cryptographic primitive, or indispensable role for hypergraphs is made.

## 7. Reproduce the numerical checks

Python 3.9 or later, standard library only:

```sh
python followup_checker.py --output followup_results.local.json
```

The script checks all 300 even difference sizes through 600, the exact pair tail, six interval bounds, sampler-ratio inequalities, the finite-counter coupling inequality, and the all-tag random-oracle union bound. Its additional toy enumerations check 38 reduced word/domain configurations and 2040 ordered distinct sequences. These toy checks are sanity checks, not substitutions for the symbolic proof.

Every pass/fail comparison uses integers or fractions, and failed checks raise explicit exceptions. Diagnostic floating-point logarithms are not used as certificates. The companion JSON is generated output. Agreement with it is computational replication, not independent cryptographic review.

## Related files

[Original derivation](technical_note.md) · [Follow-up checker](followup_checker.py) · [Generated follow-up results](followup_results.json) · [Verification record](VERIFICATION.md)

## Source references

- [Pinned matrix and sampler implementation](https://github.com/octra-labs/lite_node/blob/9e7ee19af38ba020497566ac73c268f42b20b9a4/pvac/include/pvac/crypto/matrix.hpp).
- [Pinned default parameters and domain strings](https://github.com/octra-labs/lite_node/blob/9e7ee19af38ba020497566ac73c268f42b20b9a4/pvac/include/pvac/core/types.hpp).
- [Pinned ciphertext operations](https://github.com/octra-labs/lite_node/blob/9e7ee19af38ba020497566ac73c268f42b20b9a4/pvac/include/pvac/ops/encrypt.hpp).
- [Preceding mathematical note](https://github.com/instynkt2/octra-hypergraph-analysis/blob/0b5d6d021ca4c30158a24fb9f8a3cf9e4687b091/technical_note.md).
- Bellare and Rogaway, *Random Oracles are Practical: A Paradigm for Designing Efficient Protocols*, CCS 1993, [authors' abstract](https://web.cs.ucdavis.edu/~rogaway/papers/ro-abstract.html). This is background on the modeling methodology, not a source for the new calculations here.
