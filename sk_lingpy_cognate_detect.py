# sk_lingpy_cognate_detect.py
# Standalone script for LingPy cognate detection on wordlist.tsv.
# Loads Wordlist, runs LexStat clustering, outputs cognates.csv (ID, DOCULECT, CONCEPT, IPA, COGID).

import os
import pandas as pd
import logging
from lingpy import Wordlist, LexStat
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Project root
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)

load_dotenv(os.path.join(root_dir, '.env'), override=True)

wordlist_path = os.getenv('WORDLIST_PATH', os.path.join(root_dir, 'wordlist.tsv'))
cog_threshold = float(os.getenv('COG_THRESHOLD', 0.6))
output_csv = os.getenv('OUTPUT_CSV', os.path.join(root_dir, 'cognates.csv'))

if not os.path.exists(wordlist_path):
    raise ValueError(f"Wordlist not found at {wordlist_path}")

logging.info(f"Loading wordlist from {wordlist_path}")

# Load LingPy Wordlist (standard columns: ID, DOCULECT, CONCEPT, IPA)
wl = Wordlist(wordlist_path)

# Convert spaced IPA to TOKENS column using add_entries (handles column creation)
logging.info("Converting spaced IPA to TOKENS column...")
wl.add_entries('TOKENS', 'IPA', lambda x: [seg.strip() for seg in str(x).split()] if x else [])
logging.info(f"Processed {len(wl)} entries into TOKENS.")

# LexStat for cognate detection (uses TOKENS column, skips ipa2tokens)
lex = LexStat(wl)

logging.info("Computing scorer and clustering...")
lex.get_scorer()
lex.cluster(method='sca', threshold=cog_threshold, ref='cogid')

# Output to CSV (LexStat entries as DataFrame)
df = pd.DataFrame([lex[i] for i in lex])
df.to_csv(output_csv, index=False)

# Duplicate to Python global outputs
global_outputs_dir = os.path.join(root_dir, 'Python global outputs')
os.makedirs(global_outputs_dir, exist_ok=True)
global_output_csv = os.path.join(global_outputs_dir, os.path.basename(output_csv))
df.to_csv(global_output_csv, index=False)

if 'cogid' in df.columns:
    valid_cognates = df[df['cogid'] > 0]
    num_sets = valid_cognates['cogid'].nunique() if not valid_cognates.empty else 0
else:
    num_sets = 0
logging.info(f"Saved {output_csv}: {len(df)} rows, {num_sets} cognate sets (COGID > 0); duplicated to {global_output_csv}")
