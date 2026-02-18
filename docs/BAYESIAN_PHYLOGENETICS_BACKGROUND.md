# Bayesian Phylogenetics Background

*Research notes for SK thesis methodology section*

## 1. What is Bayesian Phylogenetics?

Bayesian phylogenetics is a statistical framework for inferring evolutionary relationships (phylogenies) that:

- **Quantifies uncertainty**: Instead of producing a single "best" tree, it generates a posterior distribution of trees weighted by probability
- **Incorporates prior knowledge**: Allows integration of external information (calibration dates, geographic constraints, expected rates)
- **Handles complex models**: Can accommodate rate variation, incomplete data, and non-independence of characters

### Key Equation: Bayes' Theorem Applied to Phylogenies

```
P(Tree | Data) ∝ P(Data | Tree) × P(Tree)
```

- **P(Tree | Data)**: Posterior probability — what we want to know
- **P(Data | Tree)**: Likelihood — how probable is this data given this tree?
- **P(Tree)**: Prior — our beliefs about tree structure before seeing data

## 2. Why Bayesian Methods for Historical Linguistics?

### 2.1 Traditional Comparative Method Limitations

The comparative method (identifying regular sound correspondences → reconstructing proto-languages) is powerful but:

- **Doesn't quantify uncertainty**: Produces single reconstructions without confidence measures
- **Struggles with dialect continua**: Wave-like borrowing patterns obscure tree-like descent
- **Time-intensive**: Manual cognate judgment requires expert labor
- **Difficult to replicate**: Different scholars may reach different conclusions from same data

### 2.2 Bayesian Advantages

| Aspect | Traditional | Bayesian |
|--------|-------------|----------|
| Output | Single tree | Distribution of trees with probabilities |
| Uncertainty | Implicit, qualitative | Explicit posterior probabilities |
| Dating | Requires external evidence | Integrates dating as model parameter |
| Borrowing | Ad hoc correction | Can be modeled explicitly |
| Replicability | Variable | High (same model + data = same results) |

### 2.3 Key Papers Establishing the Field

1. **Gray & Atkinson (2003)** - "Language-tree divergence times support the Anatolian theory of Indo-European origin" (*Nature*)
   - First high-profile application to Indo-European
   - Sparked debate but demonstrated methodology

2. **Dunn et al. (2005)** - Papuan language phylogeny using structural features

3. **Greenhill et al. (2010)** - Austronesian family dating

4. **Bowern (2013)** - Critical review of methods, addresses diffusion concerns
   - Key argument: Tree signal often stronger than assumed, even in contact situations

5. **Auderset et al. (2023)** - Mixtecan Bayesian phylogenetics
   - **Direct template for SK thesis**
   - Demonstrates method in dialect continuum
   - Shows tree-like structure survives wave-like contact

## 3. Core Concepts

### 3.1 Character Coding for Linguistics

**Cognate coding** (most common approach):
- Each meaning slot (e.g., "water", "fire", "mother") is a character
- Cognate sets are coded as states (0, 1, 2, ...)
- Absence of cognate = unique state or missing data

**Example for SK:**
| Meaning | Variety A | Variety B | Variety C |
|---------|-----------|-----------|-----------|
| water   | 0         | 0         | 1         |
| fire    | 0         | 1         | 1         |
| mother  | 0         | 0         | 0         |

*Varieties A and C differ in "water" (non-cognate forms); B and C share "fire" cognate different from A.*

### 3.2 Substitution Models

**Binary models** (cognate present/absent per variety):
- Simpler, well-understood
- Lose information about cognate set structure

**Multistate models** (multiple cognate classes):
- Preserve more information
- More parameters, potential overfitting

**Ascertainment bias correction**:
- Critical for cognate data
- We only observe variable characters (no one codes "all varieties have same cognate")
- Must correct likelihood calculation to account for this

### 3.3 Clock Models

**Strict clock**: All branches evolve at same rate
- Rarely realistic for languages

**Relaxed clock**: Rate varies among branches
- **Uncorrelated lognormal**: Each branch draws rate independently
- **Autocorrelated**: Related branches have correlated rates

**Local clocks**: Different rate regimes for different clades

For SK dialects (recent divergence, similar sociolinguistic contexts), strict clock may be acceptable as first approximation.

### 3.4 Tree Priors

**Yule process**: Pure birth (speciation only)
- Good for species phylogenetics
- May not fit dialect situations well

**Birth-death**: Allows extinction
- More realistic for language families with died-out varieties

**Coalescent**: Population-genetic framework
- Emerging in linguistics for dialect-level analysis
- Models effective population sizes

### 3.5 MCMC (Markov Chain Monte Carlo)

Bayesian posteriors are typically intractable analytically → use MCMC sampling:

1. Start with random tree/parameters
2. Propose small changes (swap branches, adjust rates)
3. Accept/reject based on posterior probability ratio
4. After "burn-in", samples approximate posterior distribution

**Diagnostics**:
- **ESS (Effective Sample Size)**: Measure of independent samples (want > 200)
- **Trace plots**: Should look like "fuzzy caterpillar", not trending
- **Convergence**: Multiple chains should reach same distribution

## 4. Software: BEAST2

BEAST2 (Bayesian Evolutionary Analysis by Sampling Trees) is the standard for dated phylogenetics.

### 4.1 Key Features

- Flexible model specification via XML or BEAUti GUI
- Extensive model library via packages
- Well-documented for linguistic applications
- Active community and support

### 4.2 Workflow

1. **Data preparation**: Convert cognate matrix to BEAST-compatible format
2. **Model specification**: Choose substitution model, clock, tree prior
3. **Run analysis**: MCMC sampling (can take hours/days)
4. **Convergence check**: Tracer software
5. **Tree summarization**: TreeAnnotator → Maximum Clade Credibility tree
6. **Visualization**: FigTree, DensiTree

### 4.3 Linguistic-Specific Packages

- **BEASTLabs**: Additional models
- **BEASTling**: Python tool for preparing linguistic data
- **babel**: Specifically designed for language evolution

## 5. Addressing Borrowing/Contact

A major critique of phylogenetics in linguistics: **borrowing violates tree assumptions**.

### 5.1 Empirical Responses

**Bowern (2013)** and others show:
- Basic vocabulary (Swadesh-like lists) shows less borrowing than assumed
- Tree signal often survives contact
- Reticulation detectable but doesn't destroy signal

**Quantitative approaches**:
- Split networks visualize conflicting signals
- Delta scores measure tree-likeness
- NeighborNet shows reticulation patterns

### 5.2 Model-Based Approaches

**Explicit borrowing models**:
- Model lateral transfer as additional process
- Computationally expensive, limited implementations

**Covarion/rate heterogeneity**:
- Different rates for different meanings (some borrowed more)
- Partially captures contact effects

**For SK thesis**: Document tree-likeness metrics, acknowledge contact, use basic vocabulary to minimize issues.

## 6. Relevance to Southern Kurdish Project

### 6.1 Why Bayesian is Appropriate for SK

1. **Recent divergence**: Dialects diverged recently, uncertainty about relationships
2. **Limited data**: ~100 words per variety — Bayesian handles small datasets gracefully
3. **Debate in field**: Traditional scholars disagree on variety count — probabilistic tree provides evidence
4. **Contact present**: Kurdish varieties have ongoing contact — need method robust to this

### 6.2 Key Decisions for SK Analysis

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Character coding | Binary vs. multistate | Multistate (cognate sets from LingPy) |
| Clock model | Strict vs. relaxed | Start strict (recent divergence), test relaxed |
| Tree prior | Yule vs. coalescent | Yule (standard), consider coalescent for dialects |
| Calibration | None vs. historical | Historical events if available |
| Software | BEAST2 | Yes, with BEASTling for data prep |

### 6.3 Innovation: ASR-Assisted Pipeline

Lucas's thesis innovates by:
- Using ASR (Whisper) for initial transcription
- Automated IPA conversion
- Multi-run variability to flag uncertain items
- LingPy for semi-automated cognate detection

This addresses the **scalability problem** — traditional methods require extensive manual labor that Bayesian approaches assume is already done.

## 7. Key Terms Glossary

| Term | Definition |
|------|------------|
| **Posterior** | Probability distribution of parameters/trees after seeing data |
| **Prior** | Probability distribution before seeing data |
| **Likelihood** | Probability of data given model |
| **MCMC** | Algorithm for sampling from posterior distribution |
| **ESS** | Effective Sample Size — measure of independent samples |
| **MCC tree** | Maximum Clade Credibility tree — summary of posterior |
| **Clade** | Group of taxa (varieties) sharing common ancestor |
| **Monophyletic** | Clade including ancestor and all descendants |
| **Cognate** | Words in different languages derived from common ancestor |
| **Ascertainment bias** | Systematic bias from only observing certain characters |

## 8. Suggested Reading Order

For methodology section, read in this order:

1. **Bowern (2013)** - "The origins and development of Aboriginal Australian languages"
   - Chapter on phylogenetics — accessible introduction, addresses critiques

2. **Gray & Atkinson (2003)** - *Nature* paper
   - Short, impactful, shows what's possible

3. **Auderset et al. (2023)** - Mixtecan paper
   - **Primary model for SK thesis structure**
   - Pay attention to: model choices, how they handle contact, presentation of results

4. **BEAST2 tutorials** - [beast2.org](https://beast2.org)
   - Practical understanding before theoretical depth

5. **Drummond & Bouckaert (2015)** - "Bayesian Evolutionary Analysis with BEAST 2"
   - Comprehensive reference for methodology section

## 9. Outstanding Questions for Lucas

- [ ] Do you have access to Auderset et al. (2023) PDF? (Check email)
- [ ] What historical events could calibrate the SK tree? (Migration dates, political boundaries, etc.)
- [ ] Are there any existing SK family trees in the literature to compare against?
- [ ] What's the geographic spread of your varieties? (Map would help visualization)

---

*Compiled 2026-02-04 for thesis methodology section*
