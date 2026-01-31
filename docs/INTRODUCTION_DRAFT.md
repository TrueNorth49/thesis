# Introduction (DRAFT v1)

**Status:** First draft — needs Lucas review and refinement  
**Target:** ~500 words  
**Current:** ~520 words

---

## 1. Introduction

The classification of Southern Kurdish (SK) dialects has long posed challenges for Iranian linguistics. Early scholarship proposed relatively few distinct varieties, while more recent estimates suggest greater internal diversity among the Kurdish-speaking communities scattered across Iraq and Iran. This disagreement reflects a fundamental difficulty: SK exists not as a set of discrete languages but as a dialect continuum, where neighboring varieties blend into one another through centuries of contact, migration, and shared cultural development. Traditional comparative methods, designed for well-separated language families, struggle to quantify the probabilistic nature of such relationships.

This thesis addresses the classification problem through Bayesian phylogenetic inference—a computational framework that explicitly models uncertainty and produces probability distributions over possible dialect histories. Rather than forcing a single "correct" family tree, Bayesian methods generate posterior distributions of trees weighted by their likelihood given the data, accommodating the ambiguity inherent in dialect continua. This approach has proven valuable in similar contexts, most notably in Auderset et al.'s (2023) analysis of the Mixtecan language family, where researchers successfully identified tree-like genealogical structures amid wave-like contact signals.

The present study adapts and extends the Mixtecan methodology for SK, with several innovations suited to the low-resource linguistic context. While Auderset et al. worked with compiled lexical databases, this project begins with field-recorded audio—approximately 500 words per variety—collected directly from native speakers across multiple regions. Transcription employs a hybrid approach: automatic speech recognition (ASR) models fine-tuned for Kurdish dialects generate orthographic transcriptions, followed by IPA conversion through multilingual phonetic models. Multi-run variability analysis flags uncertain transcriptions for expert review, ensuring phonetic precision while maintaining the efficiency necessary for practical thesis timelines.

From transcriptions, the analysis proceeds through cognate detection using LingPy's LexStat algorithm, which clusters lexemes by phonetic similarity according to configurable thresholds. These clusters translate into binary state matrices suitable for input to BEAST2, a widely-used Bayesian phylogenetic modeling tool. Sensitivity analysis across different clustering thresholds tests the robustness of resulting tree topologies, while posterior distributions quantify confidence in proposed subgroups.

The research aims to answer three primary questions. First, what genealogical structure emerges from systematic phonetic comparison of SK varieties, and does it align with or challenge existing classifications? Second, to what extent do contact effects obscure or complement the tree signal—can we distinguish inherited similarities from borrowed ones? Third, how effective is an automated, ASR-assisted pipeline for phylogenetic analysis of low-resource languages, and what are its limitations?

Beyond its immediate contribution to Kurdish linguistics, this thesis offers a methodological template. The complete pipeline—from raw audio to phylogenetic trees—is implemented in Python and archived in a public GitHub repository, enabling reproduction and extension to additional datasets. As computational tools continue to mature, such automated workflows may significantly accelerate dialect documentation and classification efforts for the many understudied language varieties worldwide.

The remainder of this thesis proceeds as follows. Section 2 provides background on Southern Kurdish, dialect continua, and Bayesian phylogenetics. Section 3 details the methodology, including data collection, audio processing, transcription, cognate detection, and modeling procedures. Section 4 presents results, including phylogenetic trees and sensitivity analyses. Section 5 discusses implications and limitations, and Section 6 concludes with directions for future research.

---

## Notes for Revision

- **Needs:** Specific geographic details (which cities/regions were sampled)
- **Needs:** Citation for "early scholars argued for fewer varieties"
- **Consider:** Opening with a more compelling hook (a specific puzzle or finding?)
- **Consider:** Mentioning Prof. Haig's work if relevant to the scholarly context
- **Verify:** Is "~500 words per variety" accurate? Check data collection notes.

— Tarah 🔐 (Draft generated Jan 31, 2026)
