# Thesis Outline: Southern Kurdish Bayesian Phylogenetic Analysis

**Working Title:** Quantifying Dialect Divergence in Southern Kurdish: A Bayesian Phylogenetic Approach

**Student:** Lucas Ardelean  
**Supervisor:** Prof. Geoffrey Haig (Uni Bamberg)  
**External Reviewer:** Sarah Babinski (UZH, Bayesian specialist)  
**Deadline:** End of June 2026  
**Draft for Professor:** Mid-February 2026

---

## Structure (Following Auderset et al. 2023 Mixtecan Model)

### 1. Introduction (~500–800 words)
- **1.1** Research question and significance
- **1.2** Southern Kurdish: linguistic context and understudied status
- **1.3** The dialect continuum problem in Kurdish linguistics
- **1.4** Bayesian phylogenetics as a solution for quantifying uncertainty
- **1.5** Structure of the thesis

### 2. Background (~2000–2500 words)
- **2.1** Southern Kurdish: Geographic distribution and varieties
  - Varieties across Iraq and Iran
  - Historical scholarship on SK classification (fewer vs. more varieties debate)
- **2.2** The dialect continuum challenge
  - Tree vs. wave models in dialectology
  - Contact-induced complexity
- **2.3** Bayesian phylogenetics in linguistics
  - Brief history (biological origins → linguistic adaptation)
  - Key concepts: posterior distributions, divergence times, phylogenetic uncertainty
  - Defense of tree models in contact situations (Bowern 2013)
- **2.4** Precedents: Auderset et al. (2023) and Mixtecan
  - Their methodology
  - Their findings (tree-like structures amid wave signals)
  - What we adapt vs. what differs for SK

### 3. Methodology (~2500–3000 words)
- **3.1** Data collection
  - Fieldwork: ~500 words per variety
  - Audio/video recording methodology
  - Speaker metadata (gender, age, education, origin)
- **3.2** Audio processing pipeline
  - Segmentation with FFmpeg
  - Metadata embedding
  - Quality control measures
- **3.3** Transcription approach
  - Orthographic transcription (Whisper ASR, `razhan/whisper-base-sdh`)
  - IPA transcription (`facebook/wav2vec2-xlsr-53-espeak-cv-ft`)
  - Multi-run variability analysis for robustness
  - Reduction from 500 → <100 validated items
- **3.4** Cognate detection
  - LingPy LexStat clustering
  - JBIL/KLQ concept mapping
  - Threshold sensitivity analysis
- **3.5** Bayesian modeling
  - BEAST2 configuration
  - State coding from cognate matrices
  - Tree rooting decisions
  - Posterior sampling parameters

### 4. Results (~2000 words + figures)
- **4.1** Dataset summary
  - Number of varieties, speakers, validated lexemes
  - Transcription consistency metrics
- **4.2** Cognate detection outcomes
  - Cluster distributions
  - High-variation items flagged for review
- **4.3** Phylogenetic trees
  - Maximum clade credibility tree
  - Posterior support values
  - Divergence time estimates (if calibration available)
- **4.4** Sensitivity analysis
  - Effects of cognate threshold variation
  - Comparison across different model parameters

### 5. Discussion (~2000–2500 words)
- **5.1** Interpretation of the tree topology
  - Subgroups identified
  - Comparison with traditional classifications
  - Areas of agreement/disagreement with prior scholarship
- **5.2** Tree vs. wave signals in the data
  - Evidence for genealogical structure
  - Contact effects and their magnitude
- **5.3** Methodological contributions
  - ASR-assisted transcription in low-resource contexts
  - Automated pipeline reproducibility
  - LingPy integration with Bayesian tools
- **5.4** Limitations
  - ASR accuracy concerns
  - Sample size constraints
  - Geographic coverage gaps

### 6. Conclusion (~500 words)
- **6.1** Summary of findings
- **6.2** Implications for Kurdish linguistics
- **6.3** Future directions
  - Extension to Central Kurdish data
  - Integration of additional varieties
  - Improvements to ASR models

### References

### Appendices
- **A** Speaker metadata tables
- **B** Full wordlist with IPA transcriptions
- **C** Cognate matrices
- **D** BEAST2 configuration files
- **E** Python scripts documentation

---

## Key Differences from Auderset et al. (to highlight)

| Aspect | Auderset et al. (Mixtecan) | This Thesis (SK) |
|--------|---------------------------|------------------|
| Scale | Entire language family | Dialect-level analysis |
| Data source | Compiled lexical data | Field-recorded audio |
| Transcription | Manual curation | ASR + multi-run validation |
| Focus | Historical reconstruction | Recent dialect divergence |
| Innovation | Application to continua | Low-resource automation |

---

## Timeline to Mid-February Draft

| Week | Tasks |
|------|-------|
| Jan 29 – Feb 5 | ✓ Create outline; Draft Introduction; Literature review notes |
| Feb 5 – Feb 12 | Draft Methodology; Review Steps 1-4 implementation gaps |
| Feb 12 – Feb 15 | Compile sections; Send to Prof. Haig |

---

## Notes for Lucas

- The outline mirrors Auderset's structure but emphasizes YOUR innovations: ASR automation, low-resource pipeline, reproducible Python workflow
- Introduction draft is in `docs/INTRODUCTION_DRAFT.md`
- Consider whether divergence time estimates are feasible (need calibration points)
- The "fewer vs. more varieties" debate in early SK scholarship could be a good hook

— Tarah 🔐 (Jan 31, 2026, 2:00 AM)
