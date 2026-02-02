# Introduction Draft

*Target: ~500 words | Status: First draft*

---

Southern Kurdish (SK) presents a compelling case study for computational historical linguistics: a living language with documented dialectal variation, yet lacking the quantitative phylogenetic analysis common in better-resourced language families. While traditional comparative methods have produced conflicting classifications—with early scholars positing fewer distinct varieties than modern surveys suggest—no study has applied Bayesian phylogenetic inference to rigorously quantify the genealogical relationships among SK varieties across Iraq and Iran.

This thesis addresses that gap through a novel methodological approach: an automated pipeline that transforms raw fieldwork audio into phylogenetically informable cognate matrices, with Bayesian inference via BEAST2 producing posterior tree distributions that accommodate the inherent uncertainty of dialect continua. The approach draws methodological inspiration from Auderset et al.'s (2023) Bayesian analysis of the Mixtecan language family, which demonstrated that tree models can extract meaningful genealogical signal even in contexts traditionally characterized as "wave-like" due to extensive contact.

Three research questions guide this investigation:

1. **Genealogical structure**: What subgrouping relationships exist among SK varieties, and how do they align with or challenge existing classifications?

2. **Methodological validity**: Can Bayesian phylogenetic methods, developed primarily for family-level analysis, produce meaningful results when applied to the finer-grained variation of a dialect continuum?

3. **Automation potential**: To what extent can automated speech recognition (ASR) and IPA transcription pipelines produce data of sufficient quality for phylogenetic modeling in low-resource linguistic contexts?

The data foundation consists of approximately 500-word lists collected through in-person fieldwork with native speakers, encompassing multiple SK varieties with metadata on speaker demographics and geographic origin. These recordings undergo automated processing: segmentation via FFmpeg with embedded metadata, orthographic transcription using a Southern Kurdish-tuned Whisper model, and IPA conversion through wav2vec2. A multi-run variability analysis quantifies transcription uncertainty, flagging high-variation lexemes for expert review—an explicit acknowledgment that automation serves to augment, not replace, linguistic expertise.

Cognate detection via LingPy's LexStat algorithm produces similarity matrices mapped to standardized concept IDs (JBIL/KLQ), enabling cross-variety comparison. These matrices feed into BEAST2 for Bayesian inference, with sensitivity analysis across cognate thresholds ensuring robust conclusions.

The contributions of this work are threefold. First, it provides the first quantitative phylogenetic analysis of SK dialect divergence, addressing the "fewer vs. more varieties" debate with probabilistic evidence. Second, it demonstrates a reproducible pipeline for low-resource language analysis—from raw audio to phylogenetic trees—with all code archived on GitHub. Third, it extends the methodological precedent set by Auderset et al. (2023) from family-level classification to intra-language dialect analysis, testing the limits of Bayesian phylogenetics in contexts of maximal contact.

The thesis proceeds as follows: Chapter 2 reviews the literature on SK classification, Bayesian phylogenetics, and low-resource language processing. Chapter 3 details the methodology across six processing steps. Chapter 4 presents results including posterior trees and sensitivity analyses. Chapter 5 discusses implications for SK studies and computational linguistics. Chapter 6 concludes with limitations and future directions.

---

## Revision Notes

**What's missing / needs adding:**
- [ ] Specific geographic locations (which cities/regions were surveyed)
- [ ] Citation for early vs. modern classification debate
- [ ] Citation for Auderset et al. (2023) — get full reference from Lucas
- [ ] Number of varieties analyzed (pending final data processing)
- [ ] Brief note on why SK specifically (personal connection? research gap?)

**What to verify with Lucas:**
- Is the framing of "fewer vs. more varieties" accurate to the scholarly debate?
- Any specific scholars to cite for traditional classifications?
- Preferred emphasis: theoretical contribution vs. practical pipeline?
