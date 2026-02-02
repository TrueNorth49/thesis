# Literature Review Outline

*Chapter 2: Background & Literature Review*

---

## 2.1 Southern Kurdish: Geographic and Linguistic Context

### 2.1.1 Language Classification and Distribution
- Kurdish within the Iranian branch of Indo-European
- Tripartite division: Northern (Kurmanji), Central (Sorani), Southern (SK)
- Geographic distribution of SK: southeastern Iraq, western Iran (Kermanshah, Ilam)
- Speaker population estimates and documentation status

**Key sources to find:**
- [ ] Encyclopædia Iranica entries on Kurdish dialects
- [ ] Ethnologue/Glottolog entries
- [ ] Any dissertation-level surveys of Kurdish dialects

### 2.1.2 The Classification Debate
- Early scholarship: lumpers (fewer distinct SK varieties)
  - [ ] Find citations — MacKenzie? Other mid-20th century work?
- Modern surveys: splitters (more granular distinctions)
  - [ ] Recent dialectological work — Fattah? Hassanpour?
- Core question: genealogical splits vs. contact-induced variation

**Hook**: This debate parallels the tree vs. wave model tension that Bayesian methods can quantify.

### 2.1.3 Phonological Features of SK
- Distinctive features separating SK from CK/NK
- Isoglosses and their geographic distribution
- Relevance to cognate detection (what sound correspondences to expect)

**Practical note**: This section justifies using SK-specific ASR models and informs LingPy threshold decisions.

---

## 2.2 Bayesian Phylogenetics in Historical Linguistics

### 2.2.1 Foundations
- Bayesian inference basics: priors, likelihoods, posteriors
- MCMC methods for tree space exploration
- Why probability distributions over trees (vs. single best tree)

**Key papers:**
- [ ] Gray & Atkinson (2003) — Indo-European
- [ ] Bouckaert et al. (2012) — Indo-European homeland
- [ ] Bowern & Atkinson (2012) — methodological review

### 2.2.2 From Biology to Linguistics
- Adaptation of phylogenetic methods from evolutionary biology
- Key differences: horizontal transfer (borrowing) vs. vertical inheritance
- Character coding: cognates as binary presence/absence
- Clock models and calibration in linguistic phylogenies

### 2.2.3 Application to Dialect Continua
- Challenge: high contact rates blur tree signal
- Auderset et al. (2023) response: tree structure persists under contact
- Bowern (2013): differential diffusion doesn't erase genealogy
- When does the method break down? (critical mass of contact)

**Key argument**: Even in dialect continua, Bayesian methods can recover meaningful structure—but interpretation requires care.

---

## 2.3 The Auderset et al. (2023) Mixtecan Study

### 2.3.1 Study Overview
- Mixtecan language family: ~50 varieties, Mexico
- Goal: subgrouping within a dialect continuum
- Data: compiled lexical datasets (not fieldwork audio)

### 2.3.2 Methodology
- Character coding approach
- BEAST2 configuration (models, priors, convergence)
- Handling of uncertain cognacy

### 2.3.3 Key Findings
- Recovered tree structure despite extensive contact
- Specific subgroups identified (which?)
- Quantified tree-like vs. wave-like signal

### 2.3.4 Relevance to This Thesis
**Parallels:**
- Both: dialect continuum with contact
- Both: defending tree models against wave skepticism
- Both: Bayesian approach with posterior uncertainty

**Differences:**
| Aspect | Auderset et al. | This Thesis |
|--------|-----------------|-------------|
| Scale | Language family (~50 varieties) | Dialect (fewer varieties) |
| Data | Compiled wordlists | Raw fieldwork audio |
| Automation | None | ASR + IPA pipeline |
| Phonetics | Not emphasized | Central focus |

**What I'm adapting**: Their structure and argumentation, not their exact methods. My pipeline is more automated but smaller scale.

---

## 2.4 Low-Resource Language Processing

### 2.4.1 The Low-Resource Challenge
- Definition: limited transcribed data, no commercial tools
- SK status: some ASR models exist (Hugging Face), but sparse
- Implications for computational linguistics research

### 2.4.2 ASR for Fieldwork Data
- Whisper and fine-tuned variants
- The `razhan/whisper-base-sdh` model: training data, performance
- Transcription as approximation, not ground truth

### 2.4.3 IPA Transcription Automation
- wav2vec2-based IPA models
- Espeak-cv-ft: cross-lingual phonetic representation
- Multi-run variability: why temperature matters
- Flagging uncertainty for human review

### 2.4.4 The Hybrid Approach
- Automation for efficiency, expert validation for reliability
- When to trust the model vs. when to intervene
- Documentation and reproducibility standards

**Key argument**: This thesis demonstrates that low-resource doesn't mean low-rigor—automation can produce phylogenetically useful data with appropriate uncertainty quantification.

---

## 2.5 Synthesis: Positioning This Thesis

### Gap Identification
1. **No Bayesian phylogenetic analysis of SK**: plenty of descriptive work, no quantitative tree inference
2. **Auderset method not applied to dialect level**: their success was family-scale
3. **No audio-to-tree pipeline**: existing studies start from wordlists, not recordings

### Contribution Statement
This thesis bridges these gaps by:
- Applying Auderset-style Bayesian analysis to SK dialects
- Building an end-to-end automated pipeline (audio → cognates → trees)
- Explicitly quantifying and propagating transcription uncertainty

---

## Research Notes

### Papers to Obtain
- [ ] Auderset et al. (2023) — check Lucas's email
- [ ] Gray & Atkinson (2003) — should be accessible
- [ ] Bowern (2013) — contact and tree models
- [ ] MacKenzie on Kurdish classification
- [ ] Recent SK dialectology work

### Questions for Lucas
1. Which specific scholars represent the "fewer varieties" position?
2. Any contacts in Kurdish linguistics for validation?
3. Access to UZH linguistics library for paywalled papers?

### Grok Research Queries (for later sessions)
```
"Bayesian phylogenetics dialect continuum" site:*.edu
"Southern Kurdish classification" linguistic
"Mixtecan Auderset 2023" methodology
"low-resource ASR fieldwork linguistics"
```
