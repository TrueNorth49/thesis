# Southern Kurdish Bayesian Inference: Thesis Outline

*Mirroring Auderset et al. (2023) structure with SK-specific adaptations*

## 1. Introduction
- Problem statement: classification challenge for Southern Kurdish varieties
- Research gap: lack of quantitative phylogenetic work on SK
- Thesis contributions:
  - Novel ASR-assisted data pipeline for low-resource phonetic transcription
  - First Bayesian phylogenetic analysis of SK dialect divergence
  - Open-source reproducible methodology
- Research questions (3):
  1. What is the genealogical structure among SK varieties (Iraq/Iran)?
  2. How do Bayesian methods handle the dialect continuum signal?
  3. Can automated ASR+IPA pipelines produce reliable input for phylogenetics?
- Chapter roadmap

## 2. Background & Literature Review
### 2.1 Southern Kurdish: Geographic and Linguistic Context
- Distribution across Iraq and Iran
- Dialect classification history (early scholars: fewer varieties; modern: more)
- Phonological features distinguishing SK from Central/Northern Kurdish

### 2.2 Bayesian Phylogenetics in Historical Linguistics
- Overview of Bayesian inference for language trees
- Key studies: Gray & Atkinson (2003), Bouckaert et al. (2012)
- Application to dialect continua: challenges and solutions

### 2.3 The Auderset et al. (2023) Mixtecan Study
- Methodology summary
- Key findings: tree structure amid wave-like signals
- Relevance to SK analysis

### 2.4 Low-Resource Language Processing
- Challenges in under-documented languages
- ASR and IPA transcription for fieldwork data
- Automation vs. manual transcription trade-offs

## 3. Methodology
### 3.1 Data Collection
- Fieldwork design: ~500-word lists per variety
- Informant metadata: gender, age, education, city
- Recording equipment and protocols

### 3.2 Audio Processing Pipeline
- Segmentation via FFmpeg (timestamps from CSVs)
- Metadata embedding in WAV files
- Quality control procedures

### 3.3 Automated Transcription
- Orthographic: Whisper ASR (`razhan/whisper-base-sdh`)
- IPA: wav2vec2-xlsr-53-espeak-cv-ft
- Multi-run variability analysis (10 runs, varying temperature)
- Flagging high-variation lexemes for expert review

### 3.4 Cognate Detection
- LingPy LexStat clustering
- JBIL/KLQ concept mapping for cross-variety comparability
- Threshold sensitivity analysis

### 3.5 Bayesian Phylogenetic Modeling
- BEAST2 implementation
- Prior selection and model configuration
- MCMC convergence diagnostics
- Posterior tree summarization

## 4. Results
### 4.1 Dataset Summary
- Number of varieties, tokens, concepts retained
- Transcription accuracy metrics
- Cognate cluster statistics

### 4.2 Phylogenetic Trees
- Posterior consensus tree
- Support values and divergence estimates
- Comparison with traditional classifications

### 4.3 Sensitivity Analysis
- Effect of cognate thresholds
- ASR model comparison (if applicable)
- Robustness checks

## 5. Discussion
### 5.1 Interpreting the SK Tree
- Subgrouping implications
- Fewer vs. more varieties debate (revisiting early scholarship)
- Contact effects and wave-like signals

### 5.2 Methodological Contributions
- ASR automation for fieldwork data: lessons learned
- Reproducibility in low-resource linguistics
- Limitations and failure cases

### 5.3 Comparison with Auderset et al.
- Structural parallels
- Scale differences (family vs. dialect)
- Theoretical implications

## 6. Conclusion
- Summary of findings
- Contributions to SK studies and computational linguistics
- Future work: additional varieties, refined models, broader applications

---

## Appendices
- A: Full cognate matrices
- B: BEAST2 XML configuration
- C: Python scripts documentation
- D: Informant metadata summary

## Timeline to Mid-February Draft

| Week | Target |
|------|--------|
| Jan 29 - Feb 5 | Lit review outline, Auderset deep-read, background draft |
| Feb 5 - Feb 12 | Methodology section draft, gap analysis of Steps 1-4 |
| Feb 12 - Feb 15 | First full draft for professor review |

## Key Innovations to Highlight

1. **ASR-First Pipeline**: Most Bayesian linguistic studies use pre-existing wordlists; this project demonstrates end-to-end automation from raw audio.

2. **Multi-Run Variability**: Explicit quantification of transcription uncertainty, flagging items for expert validation.

3. **Low-Resource Reproducibility**: Full codebase on GitHub, enabling replication for other under-documented languages.

4. **Dialect Continuum Focus**: Application of family-level methods (Auderset) to intra-language variation.
