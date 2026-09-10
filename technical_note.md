# Sparse-Syndrome Uniqueness for an Idealized Octra-Parameter Ensemble

**Date:** 10 September 2026  
**Public code snapshot:** `octra-labs/lite_node`, commit `9e7ee19`  
**Status:** AI-assisted mathematical analysis, not independently peer-reviewed. The numerical inequalities have been checked using exact arithmetic. This is not a C++ audit, a Lean/Coq formalization, an IND-CPA reduction, or a security certification of a deployed network. No claim of scientific priority is made.

## 1. Statement and scope

Let H be a binary matrix with 8,192 rows and 16,384 columns. Choose its columns independently. For each column, choose weight 192 or 193 with equal probability, and choose its support uniformly conditional on that weight.

Then

\[
\Pr_H[\exists u:\ \operatorname{wt}(u)\in\{2,4,\ldots,256\},\ \operatorname{wt}(Hu)\leq258]<2^{-162}.
\]

Consequently, with probability greater than `1 - 2^-162` over this ideal matrix ensemble, the map

\[
(x,e)\longmapsto Hx\oplus e
\]

is injective simultaneously on all pairs satisfying `wt(x)=128` and `wt(e)<=129`.

This is a statement about uniqueness of a restricted internal representation. It says nothing by itself about the difficulty of recovering that representation, the confidentiality of HFHE messages, security of SHA-256, uniqueness of the implementation's salt-to-witness mapping, or security after arbitrary ciphertext operations. The exponent 162 describes a conservative upper bound on an exceptional event in the ideal matrix ensemble. It is not a security-level claim for Octra.

## 2. Connection to the inspected public code

In `pvac/include/pvac/core/types.hpp`, the `Params` defaults are `m_bits=8192`, `n_bits=16384`, `h_col_wt=192`, `x_col_wt=128`, and `err_wt=128`. These are source-code defaults, not verified parameters of a particular deployment.

In `crypto/matrix.hpp`, `gen_H` creates columns of base weight or base weight plus one. `sigma_from_H` selects 128 distinct columns at the stated defaults, XORs them and adds noise of weight 128 or 129. Its inputs include public context and a `uint64_t` salt; the numerical edge weight and plaintext are not arguments to this function.

The ideal distribution above must not be confused with the implementation. The code deterministically generates columns using SHA-256 and a sampling procedure from public context. Transferring the ensemble statement to the implementation requires a separate argument about the generator and sampler, or certification of an appropriate property for a particular matrix. This note does not assume without proof that the sampler is exactly uniform or that SHA-256 is a random oracle.

## 3. Deterministic uniqueness lemma

Assume H has no nonzero u of even weight from 2 through 256 with `wt(Hu)<=258`. Suppose two admissible pairs satisfy

\[
Hx\oplus e=Hx'\oplus e'.
\]

Then `H(x XOR x') = e XOR e'`. If `x=x'`, necessarily `e=e'`. Otherwise set `u=x XOR x'`. Because x and x' both have exactly 128 ones, u has a positive even weight no larger than 256. Also,

\[
\operatorname{wt}(Hu)=\operatorname{wt}(e\oplus e')\leq\operatorname{wt}(e)+\operatorname{wt}(e')\leq258.
\]

This contradicts the assumption, proving injectivity.

The restriction to even weights is essential. A weight-one u cannot be the difference of two selectors that each have weight 128.

## 4. Probability bound in the ideal ensemble

Write `m=8192`, `n=16384`, `b=258`. For a fixed subset S of s columns, with s even and between 2 and 256, consider the event that their XOR has weight at most b. Apply a union bound over all such subsets.

### 4.1 Two columns

Let the columns have weights `a,c` in `{192,193}`. If their supports overlap in J positions, their XOR has weight `a+c-2J`. Thus a bad pair requires

\[
J\geq\lceil(a+c-258)/2\rceil.
\]

Conditional on the first column and the two weights,

\[
\Pr[J=j]=\frac{\binom{a}{j}\binom{m-a}{c-j}}{\binom{m}{c}}.
\]

Averaging the four weight combinations and union-bounding over all pairs among 16,384 columns gives a contribution below `2^-163`. The checker evaluates this tail exactly as a rational number.

### 4.2 Larger subsets

Let Q be the distribution of a column with independent bits, each one with probability

\[
q=\frac{192.5}{8192}=\frac{385}{16384}.
\]

Let P be the ideal fixed-weight mixture. For a column v of weight w in `{192,193}`,

\[
\frac{P(v)}{Q(v)}=\frac{1}{2\Pr[\operatorname{Bin}(m,q)=w]}<18.
\]

The checker verifies the last inequality exactly by checking that each relevant binomial mass exceeds `1/36`. Hence, for s independent columns and any event A, `P(A) <= 18^s Q(A)`.

Under Q, the XOR of s columns has independent coordinates, each one with probability

\[
r_s=\frac{1-(1-2q)^s}{2}=\frac{1-(7807/8192)^s}{2}.
\]

Therefore

\[
\Pr_P[\operatorname{wt}(H1_S)\leq b]\leq18^s\Pr[\operatorname{Bin}(m,r_s)\leq b].
\]

### 4.3 Chernoff bound

For `r>b/m`,

\[
\Pr[\operatorname{Bin}(m,r)\leq b]\leq\left(\frac{mr}{b}\right)^b\left(\frac{m(1-r)}{m-b}\right)^{m-b}.
\]

The checker performs the comparison using exact rational arithmetic. Splitting the larger even support sizes into four ranges gives a contribution below `2^-200` for each range. Thus

\[
\Pr[H\text{ is bad}]<2^{-163}+4\cdot2^{-200}<2^{-162}.
\]

## 5. Exact XOR composition

For any binary matrix H,

\[
(Hx_1\oplus e_1)\oplus(Hx_2\oplus e_2)=H(x_1\oplus x_2)\oplus(e_1\oplus e_2).
\]

The inspected ciphertext-compaction code XORs syndrome fields. This property belongs to binary linear maps generally; it is not unique to hypergraphs.

The base uniqueness theorem cannot automatically be applied after arbitrary composition because the selector weight and error bound change.

## 6. What the result does not establish

The injectivity result concerns x and e, not the numerical ciphertext weight or plaintext. It does not prove inversion hardness, an LPN reduction, semantic binding to value-bearing data, IND-CPA security, or a production security level.

The actual implementation derives H deterministically from hashing and sampling logic. Establishing that a particular generated matrix satisfies the required restricted-distance property is a separate problem.

At fixed public context, a 64-bit salt gives the syndrome generator at most `2^64` salt inputs. This observation concerns that internal randomness only; it is not a statement that HFHE messages or keys have 64-bit security.

## 7. Algebraic limitation: XOR versus odd-characteristic addition

For odd p, there is no nonzero map T from `F_p` to a binary vector space, depending only on the field value, such that

\[
T(a+b)=T(a)\oplus T(b)
\]

for all a,b. Given any v, choose `a=v/2`. Then `T(v)=T(a+a)=T(a) XOR T(a)=0`.

So a nontrivial deterministic fully additive binary tag of a field value alone cannot have this form. This does not rule out randomized commitments, computation-history tags, additional metadata or separate proof systems.

## 8. Reproduction

Run:

```sh
python sparse_syndrome_checker.py --output check_results.json
```

The checker uses only Python's standard library and exact integer/Fraction arithmetic. It is not Monte Carlo: it verifies the finite numerical inequalities used in the derivation. It does not execute or audit the Octra C++ implementation.

## 9. Conclusion

The result establishes a narrowly scoped positive property of an ideal sparse binary encoding at parameters drawn from a public Octra snapshot: with high probability over matrix selection, an admissible sparse witness has a unique syndrome representation.

It does not establish a new general cryptographic primitive, a necessary role for hypergraphs, a production security level, or full HFHE confidentiality. The main next questions concern the actual matrix generator, the relationship to ciphertext semantics, and preservation of relevant properties under composition.

## Public code references

- https://raw.githubusercontent.com/octra-labs/lite_node/9e7ee19/pvac/include/pvac/core/types.hpp
- https://raw.githubusercontent.com/octra-labs/lite_node/9e7ee19/pvac/include/pvac/crypto/matrix.hpp
- https://raw.githubusercontent.com/octra-labs/lite_node/9e7ee19/pvac/include/pvac/ops/encrypt.hpp
