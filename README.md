# Southern Kurdish Bayesian Inference Project: Processes, Steps, Rationales, and Comparisons

## Project Overview

The Southern Kurdish (SK) Bayesian Inference Project analyzes dialect divergence among SK varieties spoken across Iraq and Iran. The project utilizes field-recorded audio data (approximately 500 words per dataset) transcribed in both orthographic and International Phonetic Alphabet (IPA) formats, with a strong emphasis on phonetic accuracy in a low-resource language context. Note that the initial wordlist of 500 words will be paired down to fewer than 100 words after demonstrating that the process works effectively; once paired down, manual checks will be made of the IPA transcriptions to ensure accuracy. The workflow is sequential and iterative, incorporating automation for efficiency through tools such as Hugging Face ASR models, LingPy for cognate detection, and BEAST2 for Bayesian phylogenetic modeling. This approach supports probabilistic analysis of dialectal variations, drawing inspiration from methods employed by researchers such as those at the University of Zurich. The project is structured for a master's thesis, with all code and documentation archived in a public GitHub repository for reproducibility. Factual errors may exist in the .py scripts, as noted in their documentation.

Key objectives include:
- Quantifying genealogical splits among SK varieties using Bayesian trees. Note that early scholars of SK argued for fewer varieties than some modern estimates suggest.
- Measuring lexical influences through similarity analysis (though LingPy is not designed for direct cross-family borrowing detection; affinities are assessed via metrics like similarity scores rather than phylogenetic rooting).
- Ensuring phonetic precision via orthographic and IPA transcriptions, supplemented by expert validation for ambiguous lexemes.
- Promoting automation to address computational and logistical constraints in low-resource linguistic settings.

This overview is derived from the project's README.md and supporting scripts (e.g., `sk_asr_segmentation.py`, `sk_ipa_transcription.py`, `sk_lingpy_cognate_detect.py`).

While the current implementation includes references to Central Kurdish (CK) in examples (e.g., ASR models), the primary focus is on Southern Kurdish (SK). The GitHub README.md serves to highlight the overall processes for SK analysis, functioning as a template and test-case for extending the method to additional datasets, such as existing CK data.

## Processes and Steps

The workflow consists of six primary steps, as documented in the README.md with adjustments for data collection. Each step includes a description, the tools and scripts involved (where applicable), and the rationale/purpose, illustrating how it contributes to the project's objectives of dialect divergence analysis and lexical affinity assessment.

### Step 1: Data Collection (Status: Completed)
**Description**: Wordlists were collected in person through survey work with informants. Both audio and video recordings were made of each wordlist during these sessions.

**Tools/Scripts**: Manual survey tools; audio/video recording equipment.

**Rationale/Purpose**: In-person data collection ensures high-quality, contextually rich recordings directly from native speakers, capturing natural pronunciation and variations essential for accurate transcription and analysis in a low-resource language like SK. This foundational step establishes the raw dataset, enabling subsequent automated processing while preserving informant-specific details for validation.

### Step 2: Audio Processing (Status: Implemented)
**Description**: Raw field-recorded audio files are segmented according to timestamps from TSV/CSV files (e.g., `Halabja_M_1990.csv`). Segmentation is performed using FFmpeg, with speaker metadata (e.g., gender, age, education, city of origin) embedded directly into the resulting WAV files. Outputs include a `segments/` folder per dataset, `mapping.csv` (linking timestamps to audio files), and `metadata.csv` (containing segment paths and metadata). The script `sk_asr_segmentation.py` enables batch processing across directories containing "process" in their name.

**Tools/Scripts**: FFmpeg for segmentation and metadata embedding; pandas for CSV handling; python-dotenv for configuration.

**Rationale/Purpose**: Audio segmentation isolates individual lexemes from continuous recordings, enabling precise transcription and analysis at the word level. Embedding metadata preserves essential contextual information for potential sociolinguistic correlations. In low-resource languages such as SK, where data are often unstructured or noisy, this automated step reduces manual labor, enhances reproducibility, and prepares standardized files (e.g., `JBIL_001_one_Hala01.wav`) for downstream processing.

### Step 3: Transcription (Status: Implemented)
**Description**: Segmented audio is transcribed orthographically using Hugging Face ASR models (e.g., `razhan/whisper-base-sdh` for SK-specific dialects. IPA transcriptions are subsequently generated using `facebook/wav2vec2-xlsr-53-espeak-cv-ft`. Multi-run variability analysis is conducted via `sk_multi_ipa.py` (e.g., 10 runs with varying temperatures for robustness), producing consolidated CSVs such as `{dataset_name}_ipa_transcriptions.csv` and `{dataset_name}_ipa_variations.csv`. Scripts including `sk_ipa_transcription.py` and `sk_ipa_variation_analysis.py` handle merging and inconsistency detection.

**Tools/Scripts**: Transformers library for ASR pipelines; torch for GPU acceleration; pandas for CSV merging and analysis.

**Rationale/Purpose**: Orthographic transcription provides a readable baseline, while IPA ensures phonetic fidelity essential for detecting subtle sound changes in dialect continua. Multi-run analysis accounts for ASR variability in low-resource settings, flagging high-variation lexemes for expert review. The use of SK-tuned models improves accuracy over generic alternatives and supports the project's focus on phonetic precision, thereby generating reliable datasets suitable for phylogenetic modeling.

### Step 4: Wordlist Preparation and Cognate Detection (Status: Implemented)
**Description**: IPA transcriptions are consolidated into a standardized wordlist (`wordlist.tsv`) using `sk_consolidate_wordlist.py`, with lexical items mapped to JBIL/KLQ concept IDs from `consolidated list.csv` for cross-dataset comparability. Cognate detection is performed via LingPy in `sk_lingpy_cognate_detect.py`, yielding `cognates.csv` files containing cluster IDs and similarity scores. Duplicate, missing, and extraneous concept checks are documented in `wordlist_check.txt`.

**Tools/Scripts**: LingPy for LexStat clustering; pandas for data manipulation and validation.

**Rationale/Purpose**: Concept standardization via JBIL/KLQ mappings ensures semantic comparability across varieties, mitigating issues of drift in dialect analysis. Cognate detection converts raw IPA data into binary matrices suitable for phylogenetics, while quantifying similarities and potential borrowings. Threshold-based clustering enables sensitivity analysis, bridging phonetic data to probabilistic modeling. This automated step enhances efficiency in low-resource contexts, replacing labor-intensive manual processes with reproducible computational outputs.

### Step 5: BEAST2 Modeling (Status: Pending)
**Description**: Cognate matrices from Step 4 are converted into state-coded formats for Bayesian phylogenetic inference in BEAST2 (note: the .py script for state coding does not yet exist). During the state coding process or prior, cognates will need to be identified so that states are properly coded. This step produces phylogenetic trees, divergence time estimates, and posterior probabilities. The tree will likely be rooted. Scripts (to be developed) will handle matrix conversion and model execution, incorporating LingPy threshold variations for sensitivity testing.

**Tools/Scripts**: BEAST2 for phylogenetic modeling; potential Python wrappers for input preparation.

**Rationale/Purpose**: Bayesian inference provides probabilistic quantification of dialect splits and lexical affinities, accommodating uncertainty inherent in dialect continua (e.g., contact-induced noise). Posterior distributions enable estimation of divergence timelines and borrowing rates, directly supporting the project's core objectives. Sensitivity analysis ensures model robustness, elevating the analysis from descriptive similarity metrics to rigorous inferential conclusions.

### Step 6: Validation and Thesis Write-Up (Status: Pending)
**Description**: High-variation items undergo manual expert review, followed by sensitivity analysis (e.g., varying cognate thresholds). Results are synthesized into a thesis document, including quantitative metrics such as cluster sizes and borrowing rates.

**Tools/Scripts**: Manual review tools; potential code-based statistics.

**Rationale/Purpose**: Expert validation addresses potential biases in ASR or cognate detection, ensuring data and model reliability. Sensitivity testing enhances robustness, while the write-up integrates all steps into a coherent narrative on dialect divergence and affinities. This final stage fulfills the thesis requirements and supports future extensions (e.g., additional varieties or datasets).

## Comparison with Auderset et al. (2023) Mixtecan Bayesian Project

### Overall Goals
- **Southern Kurdish Bayesian Inference Project**: Focuses on quantifying recent dialect divergence in a living, low-resource language (SK), with analysis of lexical affinities through similarity metrics. Objectives emphasize phonetic accuracy, computational automation, and practical thesis deliverables such as trees and metrics.
- **Auderset et al. (2023)**: Seeks to subgroup an entire language family (Mixtecan) within a dialect continuum, evaluating the applicability of Bayesian phylogenetics relative to traditional methods. Goals center on historical reconstruction, quantification of tree- versus wave-like patterns, and methodological contributions to historical linguistics.

Both projects apply Bayesian phylogenetics to dialect-heavy contexts to elucidate genealogical relationships amid ongoing contact; however, the SK project is more applied and resource-constrained, while the Mixtecan study is theoretical and family-scale.

### Similarities
- **Methodological Core**: Both rely on Bayesian phylogenetics (e.g., BEAST-like tools) to model uncertainty in dialect continua, producing posterior tree distributions that accommodate contact-related noise. Lexical/cognate data serve as primary input, and both defend tree models against overestimations of diffusion (consistent with Bowern 2013).
- **Handling Dialect Continua**: Both identify tree-like structures amid wave-like signals; cognate detection in the SK project parallels the Mixtecan approach to differential diffusion.
- **Data-Driven Insights**: Both uncover potential new subgroups/divergences and underscore the influence of data preparation methods (e.g., LingPy thresholds versus primary data gathering effects).
- **Complementary to Tradition**: Phylogenetics is positioned as enhancing rather than replacing comparative methods, with both advocating hybrid tree-wave frameworks.

### Differences
- **Scope and Focus**: The SK project targets dialect-specific variation, prioritizing phonetics via modern audio processing; the Mixtecan study addresses family-level historical reconstruction using compiled lexical data without emphasis on audio or phonetics.
- **Data Sourcing/Preparation**: The SK project automates from raw audio (ASR, multi-run IPA) for low-resource efficiency, introducing potential biases mitigated by variability checks; the Mixtecan study relies on manually curated or compiled data, highlighting organizational impacts without automation.
- **Tools and Innovation**: The SK project employs a Python-centric stack (LingPy, transformers) for reproducibility; the Mixtecan study uses Bayesian tools in a more traditional linguistic framework, innovating in application to continua without AI-assisted transcription.
- **Challenges Addressed**: The SK project tackles transcription variability in low-resource settings; the Mixtecan study emphasizes overestimation of contact and critiques of alternative models (e.g., glottometry).
- **Outputs/Implications**: The SK project produces practical metrics for a thesis; the Mixtecan study advances theoretical debates and calls for broader methodological scrutiny.

In summary, the Southern Kurdish Bayesian Inference Project adapts the Mixtecan approach to a computational, phonetically oriented framework suitable for a low-resource language, rendering it more accessible while introducing new variables (e.g., ASR accuracy). Both maintain a commitment to Bayesian rigor in contact-prone linguistic environments.

