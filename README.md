# Inside Octra’s Hypergraph Layer: What Can Be Proven About Its Syndromes

*A code-grounded research note on a conditional uniqueness result—and what it does not establish.*

When I examine a cryptographic design, I want to distinguish three things: what the implementation does, what its mathematics establishes, and what remains to be demonstrated.

That is the approach I took to one component of Octra’s public PVAC implementation: its sparse, hypergraph-based syndrome construction.

The question is precise:

**Can two different admissible internal representations produce the same syndrome?**

An AI-assisted analysis yields a positive result under an explicitly defined ideal model. At the parameters examined, the probability of selecting a matrix that admits such an ambiguity is less than 2⁻¹⁶².

That is a statement about a restricted encoding—not “162-bit security for Octra,” and not a proof of HFHE confidentiality.

Here is the argument and why that distinction matters.

## 1. Start with the construction

This note examines `octra-labs/lite_node` at commit `9e7ee19`, rather than making a claim about whichever version is currently deployed.

The default parameters in `core/types.hpp` describe a binary matrix with 8,192 rows and 16,384 columns, a base column weight of 192, a selector weight of 128, and a base error weight of 128. These are source-code defaults, not independently confirmed deployment parameters. [1]

A binary incidence matrix can describe a hypergraph: rows represent vertices, while the ones in a column indicate which vertices belong to that hyperedge.

In the inspected construction, a column has 192 or 193 ones. Syndrome generation selects 128 distinct columns, XORs them together, and adds an error vector containing 128 or 129 ones. [2]

In mathematical shorthand:

**σ = Hx ⊕ e**

Here, H is the matrix, x identifies the selected columns, e is the error vector, and σ is the resulting syndrome. XOR means addition modulo two: repeated contributions cancel in pairs.

The pair (x, e) is the internal representation, or “witness,” considered below. It is not the plaintext.

## 2. The model-level result

The analysis makes a specific idealization: columns of H are independent; each has weight 192 or 193 with equal probability; and, conditional on its weight, its support is uniformly distributed.

Under that model, the derivation gives the following result:

> With probability greater than 1 − 2⁻¹⁶² over the choice of H, the map (x, e) → Hx ⊕ e is injective simultaneously for every pair with exactly 128 ones in x and at most 129 ones in e.

“Injective” means two different admissible pairs cannot produce the same output.

This is not merely a claim about two randomly chosen inputs. Once H has the stated property, it holds across the entire restricted domain—including correlated choices of x and e.

The phrase **restricted domain** is essential. The result does not say the matrix has no collisions on arbitrary binary inputs.

## 3. Why uniqueness follows

Suppose two admissible pairs produce the same syndrome:

**Hx ⊕ e = Hx′ ⊕ e′**

Rearranging gives:

**H(x ⊕ x′) = e ⊕ e′**

Write u = x ⊕ x′.

If x and x′ differ, u must have a positive, even number of ones, between 2 and 256. That follows because both selectors contain exactly 128 ones.

Meanwhile, each error vector contains at most 129 ones. Their XOR therefore contains at most 258.

Every collision would consequently require a nonzero u satisfying both conditions:

**wt(u) ∈ {2, 4, …, 256}**

**wt(Hu) ≤ 258**

Here, wt simply counts the ones in a binary vector.

If H has no such u, different admissible pairs cannot collide. If x = x′ instead, the original equation immediately gives e = e′.

That establishes the deterministic part of the argument. The remaining question is how often an ideal random H fails the required condition.

A small detail matters: the even-weight restriction cannot be dropped. A single column has only 192 or 193 ones, but a single-column difference cannot arise between two selectors that both have weight 128.

## 4. Where the probability bound comes from

The calculation separates pairs of columns from larger subsets.

For two columns with weights a and b and an overlap of J positions, their XOR has weight:

**a + b − 2J**

For example, two weight-192 columns would need an overlap of at least 63 positions to produce an XOR of weight 258 or less.

The overlap probability can be computed exactly using a hypergeometric distribution. Accounting for all four combinations of column weights and every pair among 16,384 columns gives:

**Probability of any qualifying two-column event < 2⁻¹⁶³.**

For larger even subsets, the argument uses a comparison with independent Bernoulli columns, a Chernoff tail bound, and a union bound over the relevant subsets.

The change of probability model is explicitly accounted for; it is not assumed to be free. The even support sizes from 4 through 256 are divided into four groups, each contributing less than 2⁻²⁰⁰.

Combining the bounds gives:

**Pr[H fails the condition] < 2⁻¹⁶³ + 4 × 2⁻²⁰⁰ < 2⁻¹⁶².**

The accompanying Python checker verifies the numerical inequalities using exact integers and rational arithmetic. Those checks passed.

This is not a Monte Carlo experiment. No conclusion is extrapolated from a sample of randomly generated matrices. The program checks the finite inequalities used in the argument.

It is also not a proof-assistant formalization. The mathematical reasoning and its application remain subject to independent review.

## 5. What this tells us about the representation

The result provides a concrete structural property: an ideal matrix from this ensemble can distinguish every admissible sparse witness, despite having more columns than rows.

There is no contradiction. A linear map can have collisions over its full input space while remaining injective on a sufficiently restricted subset.

There is also an exact composition identity:

**(Hx₁ ⊕ e₁) ⊕ (Hx₂ ⊕ e₂) = H(x₁ ⊕ x₂) ⊕ (e₁ ⊕ e₂).**

Two syndromes can therefore be combined into the syndrome of the XOR of their witnesses without knowing those witnesses. The inspected ciphertext-compaction code combines syndrome fields through XOR. [3]

These are legitimate properties to analyze. They give the representation a precise mathematical interpretation.

But they are not unique to hypergraphs. The composition identity holds for binary linear maps generally, and this analysis does not establish that the particular sparse representation is necessary or more efficient than alternatives.

## 6. Keep the conclusion within its scope

**Uniqueness is not secrecy.**

A function can be perfectly injective and trivial to invert. This result excludes alternative admissible witnesses for a good H; it does not establish the computational cost of recovering the unique witness.

It therefore does not provide a hardness reduction for HFHE or an estimate of the work required to recover a message.

**The ideal ensemble is not the deployed generator.**

The implementation constructs H deterministically using SHA-256 and a sampling procedure, rather than drawing directly from the ideal ensemble. Moving from this theorem to that generator requires a separate argument, or an appropriate check of a particular matrix. [2]

The numerical checker does not perform that check.

**A unique witness is not automatically a commitment to the message.**

The theorem concerns x and e. The inspected `sigma_from_H` function does not take the numerical edge weight or plaintext as an argument. A claim about binding those values requires an additional, explicitly verified relationship. [2]

This note does not establish that relationship. Nor does it infer, solely from this function’s signature, what every surrounding protocol mechanism does.

**Composition changes the domain.**

After XOR aggregation, the selector need not have weight 128, and the combined error may exceed weight 129. The original uniqueness theorem cannot simply be reused indefinitely.

XOR composition remains algebraically correct. Preservation of uniqueness under a particular sequence of operations is a separate question.

The technical supplement also addresses two related limits: the salt input’s domain and why binary XOR cannot, by itself, serve as a nontrivial deterministic additive tag of a value in an odd-characteristic field.

## 7. The useful next step

For me, the value of this analysis is not an opportunity to label the entire system “proven.” It is a way to make further investigation more precise.

At the encoding level, there is a concrete conditional result and a reproducible numerical check.

At the implementation level, the next task is to connect the ideal distribution to the actual generator and sampler.

At the protocol level, the task is to identify which security property uses the witness’s uniqueness, how that relationship is enforced, and what survives subsequent ciphertext operations.

Those are different questions. Answering one does not silently answer the others.

## Conclusion

My takeaway is narrow but positive:

**At parameters taken from a public Octra snapshot, an idealized sparse-syndrome construction has a high-probability uniqueness property that can be supported by a mathematical argument and exact-arithmetic checks.**

That provides a concrete result about the encoding layer. It is neither a proof of full HFHE security nor evidence that hypergraphs are indispensable.

A useful technical discussion should be able to hold both conclusions at once: recognize a property that has been established within a model, and keep its implications within the boundaries of that model.

*Methodology: AI-assisted analysis of public source code. The derivation has not been independently peer-reviewed, and no claim of scientific priority is made. The accompanying checker verifies numerical inequalities, not Octra’s C++ implementation or a deployed network.*

---

## Public source references

All paths below are pinned to commit `9e7ee19`:

```text
[1] https://raw.githubusercontent.com/octra-labs/lite_node/9e7ee19/pvac/include/pvac/core/types.hpp
[2] https://raw.githubusercontent.com/octra-labs/lite_node/9e7ee19/pvac/include/pvac/crypto/matrix.hpp
[3] https://raw.githubusercontent.com/octra-labs/lite_node/9e7ee19/pvac/include/pvac/ops/encrypt.hpp
```

Supporting files: `technical_note.md`, `sparse_syndrome_checker.py`, and `check_results.json`.
