# sk_lingpy_wordlist_prep.py
# Standalone batch script to prepare LingPy wordlist from IPA CSVs + mapping.csv.
# Outputs wordlist.tsv (tab-separated): ID, DOCULECT, CONCEPT, IPA.

import os
import pandas as pd
import logging
import re
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Project root
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
processed_root = os.path.normpath(os.path.join(root_dir, 'Audio_Processed'))

if not os.path.exists(processed_root):
    raise ValueError(f"Audio_Processed not found at {processed_root}")

# Target dirs with .env and ipa CSV
target_dirs = [
    d for d in os.listdir(processed_root)
    if os.path.isdir(os.path.join(processed_root, d))
    and 'process' in d.lower()
    and os.path.exists(os.path.join(processed_root, d, '.env'))
]

logging.info(f"Found target directories: {target_dirs}")

all_rows = []
global_id = 1

for target_dir in target_dirs:
    dataset_dir = os.path.join(processed_root, target_dir)
    load_dotenv(os.path.join(dataset_dir, '.env'))
    
    dataset_name_raw = os.getenv('DATASET_NAME', os.path.basename(dataset_dir))
    dataset_name = dataset_name_raw.lower().replace(' ', '').replace('process', '').strip()
    
    ipa_csv = os.path.join(dataset_dir, f"{dataset_name}_ipa_transcriptions.csv")
    mapping_csv = os.path.join(dataset_dir, 'mapping.csv')
    
    if not os.path.exists(ipa_csv) or not os.path.exists(mapping_csv):
        logging.warning(f"Missing CSV in {dataset_dir}, skipping")
        continue
    
    # Load CSVs
    ipa_df = pd.read_csv(ipa_csv)
    mapping_df = pd.read_csv(mapping_csv)
    
    # Clean mapping audio_file for merge
    mapping_df['audio_file_clean'] = mapping_df['audio_file'].astype(str).str.replace('.wav', '', regex=False).str.strip()
    
    # Merge on lexeme_id == audio_file_clean
    merged = pd.merge(ipa_df, mapping_df, left_on='lexeme_id', right_on='audio_file_clean', how='inner')
    
    # Clean CONCEPT from 'Name'
    def clean_concept(name):
        if pd.isna(name):
            return ''
        name = str(name)
        # Remove id prefixes/parentheses/spaces
        cleaned = re.sub(r'^[$(]?\d+(?:\.\d+)?[$\)]?[- ]*|[$(][^)]*[$\)]|[- ]*$', '', name).strip().lower()
        return cleaned
    
    merged['CONCEPT'] = merged['Name'].apply(clean_concept)
    
    # DOCULECT
    dataset_code = os.getenv('DATASET_CODE', dataset_name)
    kurdish_variety = os.getenv('KURDISH_VARIETY', 'CK')
    doculect = f"{dataset_code}_{kurdish_variety}"
    
    # IPA
    merged['IPA'] = merged['ipa_transcription'].fillna('')
    
    # Select/append
    dataset_rows = merged[['CONCEPT', 'IPA']].copy()
    dataset_rows['DOCULECT'] = doculect
    dataset_rows['ID'] = range(global_id, global_id + len(dataset_rows))
    global_id += len(dataset_rows)
    
    all_rows.append(dataset_rows[['ID', 'DOCULECT', 'CONCEPT', 'IPA']])
    
    logging.info(f"Added {len(dataset_rows)} rows from {dataset_dir} (doculect: {doculect})")

if not all_rows:
    logging.warning("No data found")
else:
    wordlist_df = pd.concat(all_rows, ignore_index=True).sort_values('ID')
    
    output_dir = os.getenv('OUTPUT_DIR', root_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'wordlist.tsv')
    
    wordlist_df.to_csv(output_path, sep='\t', index=False)

    # Duplicate to Python global outputs
    global_outputs_dir = os.path.join(root_dir, 'Python global outputs')
    os.makedirs(global_outputs_dir, exist_ok=True)
    global_output_path = os.path.join(global_outputs_dir, 'wordlist.tsv')
    wordlist_df.to_csv(global_output_path, sep='\t', index=False)
    logging.info(f"Saved LingPy wordlist to {output_path} ({len(wordlist_df)} rows) and duplicated to {global_output_path}")
