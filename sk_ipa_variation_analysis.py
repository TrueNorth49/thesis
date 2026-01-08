# sk_ipa_variation_analysis.py
# Standalone script to analyze variations in multi-run IPA CSV.
# Discovers *process dirs, loads _multi_ipa.csv, identifies/computes variations per row, saves report CSV.

import os
import pandas as pd
import logging
from collections import Counter
from dotenv import load_dotenv
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Project root
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
processed_root = os.path.normpath(os.path.join(root_dir, 'Audio_Processed'))

if not os.path.exists(processed_root):
    raise ValueError(f"Audio_Processed not found at {processed_root}")

# Target dirs with .env (assume multi_ipa.csv exists)
target_dirs = [
    d for d in os.listdir(processed_root)
    if os.path.isdir(os.path.join(processed_root, d))
    and 'process' in d.lower()
    and os.path.exists(os.path.join(processed_root, d, '.env'))
]

logging.info(f"Found target directories: {target_dirs}")

def process_dataset_dir(dataset_dir: str) -> None:
    load_dotenv(os.path.join(dataset_dir, '.env'))
    
    dataset_name_raw = os.getenv('DATASET_NAME', os.path.basename(dataset_dir))
    dataset_name = dataset_name_raw.lower().replace(' ', '').replace('process', '').strip()
    
    multi_ipa_csv = os.path.join(dataset_dir, f"{dataset_name}_multi_ipa.csv")
    if not os.path.exists(multi_ipa_csv):
        logging.warning(f"No _multi_ipa.csv in {dataset_dir}, skipping")
        return
    
    df = pd.read_csv(multi_ipa_csv)
    logging.info(f"Loaded {len(df)} rows from {multi_ipa_csv}")
    
    # IPA run columns
    ipa_cols = [col for col in df.columns if col.startswith('ipa_run')]
    num_runs = len(ipa_cols)
    if num_runs == 0:
        logging.warning("No ipa_run columns, skipping")
        return
    
    variation_threshold = int(os.getenv('VARIATION_THRESHOLD', 1))
    
    results = []
    for idx, row in df.iterrows():
        ipa_runs = row[ipa_cols].tolist()
        unique_ipas = [ipa for ipa in ipa_runs if ipa]  # Ignore empty
        unique_set = set(unique_ipas)
        has_variation = len(unique_set) > variation_threshold
        
        if has_variation:
            counter = Counter(unique_ipas)
            details = '; '.join([f"'{ipa}': {count}x" for ipa, count in sorted(counter.items())])
            logging.info(f"Variation in {row['lexeme_id']} ({row['english_word']}): {details}")
        else:
            details = ''
        
        results.append({
            'lexeme_id': row['lexeme_id'],
            'english_word': row['english_word'],
            'has_variation': has_variation,
            'unique_transcriptions': sorted(list(unique_set)),
            'variation_details': details
        })
    
    df_variations = pd.DataFrame(results)
    output_csv = os.path.join(dataset_dir, f"{dataset_name}_ipa_variations.csv")
    df_variations.to_csv(output_csv, index=False)

    # Duplicate to Python global outputs
    global_outputs_dir = os.path.join(root_dir, 'Python global outputs')
    global_dataset_dir = os.path.join(global_outputs_dir, os.path.basename(dataset_dir))
    os.makedirs(global_dataset_dir, exist_ok=True)
    global_output_csv = os.path.join(global_dataset_dir, f"{dataset_name}_ipa_variations.csv")
    df_variations.to_csv(global_output_csv, index=False)
    logging.info(f"Saved variations report to {output_csv} ({len(df_variations)} rows, {df_variations['has_variation'].sum()} variations) and duplicated to {global_output_csv}")

# Process
for target_dir in target_dirs:
    dataset_dir = os.path.join(processed_root, target_dir)
    process_dataset_dir(dataset_dir)

logging.info("Variation analysis complete.")
