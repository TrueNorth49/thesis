# Multi-Run IPA Transcription Script
# Standalone script to run IPA pipeline multiple times on segments for variability analysis.
# Outputs lean CSV: lexeme_id, #, english_word, ipa_run1 to ipa_runN (N=NUM_IPA_RUNS).
# Mirrors discovery/logic from sk_ipa_transcription.py; batch_size=16 for efficiency.

from transformers import pipeline
import torch
import os
import pandas as pd
import logging
import json
import subprocess
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Compute project root
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
processed_root = os.path.normpath(os.path.join(root_dir, 'Audio_Processed'))

if not os.path.exists(processed_root):
    raise ValueError(f"Audio_Processed not found at: {processed_root}")

# Discover target dirs
target_dirs = [
    d for d in os.listdir(processed_root)
    if os.path.isdir(os.path.join(processed_root, d))
    and 'process' in d.lower()
    and os.path.exists(os.path.join(processed_root, d, 'segments'))
    and os.path.exists(os.path.join(processed_root, d, '.env'))
]

logging.info(f"Found target directories: {target_dirs}")

ipa_model = 'facebook/wav2vec2-xlsr-53-espeak-cv-ft'
device = 0 if torch.cuda.is_available() else -1
logging.info(f"Device: {'cuda:0' if device == 0 else 'cpu'}")

def get_metadata(file_path: str) -> dict:
    file_path = os.path.normpath(file_path)
    if not os.path.exists(file_path):
        return {}
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_entries', 'format_tags', file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {}
    try:
        data = json.loads(result.stdout)
        return data.get('format', {}).get('tags', {})
    except json.JSONDecodeError:
        return {}

def process_dataset_dir(dataset_dir: str) -> None:
    load_dotenv(os.path.join(dataset_dir, '.env'))
    
    dataset_name_raw = os.getenv('DATASET_NAME', os.path.basename(dataset_dir))
    dataset_name = dataset_name_raw.lower().replace(' ', '').replace('process', '').strip()
    
    segments_folder = os.path.normpath(os.path.join(dataset_dir, os.getenv('SEGMENTS_FOLDER', 'segments')))
    metadata_csv_path = os.path.join(dataset_dir, os.getenv('METADATA_CSV', 'metadata.csv'))
    
    # Load audio_files
    audio_files = []
    if os.path.exists(metadata_csv_path):
        metadata_df = pd.read_csv(metadata_csv_path)
        if 'audio_path' in metadata_df.columns:
            audio_files = [os.path.normpath(p) for p in metadata_df['audio_path'].tolist()]
        logging.info(f"Loaded {len(audio_files)} from {metadata_csv_path}")
    
    if not audio_files and os.path.exists(segments_folder):
        audio_files = sorted([os.path.normpath(os.path.join(segments_folder, f)) for f in os.listdir(segments_folder) if f.endswith('.wav')])
        logging.info(f"Loaded {len(audio_files)} from {segments_folder}")
    
    if not audio_files:
        logging.warning(f"No audio in {dataset_dir}")
        return
    
    num_runs = int(os.getenv('NUM_IPA_RUNS', 10))
    logging.info(f"Running IPA {num_runs} times on {len(audio_files)} files")
    
    all_runs = []
    for run in range(1, num_runs + 1):
        temperature = 0.0 if run == 1 else 0.5  # Deterministic first, variable others
        ipa_pipe = pipeline("automatic-speech-recognition", model=ipa_model, device=device, 
                            generate_kwargs={"temperature": temperature})
        
        try:
            results = ipa_pipe(audio_files, batch_size=16)
            run_texts = [r['text'].strip() if isinstance(r, dict) and 'text' in r and isinstance(r['text'], str) else '' for r in results]
        except Exception as e:
            logging.error(f"Run {run} error: {e}")
            run_texts = [''] * len(audio_files)
        
        all_runs.append(run_texts)
    
    # Build df
    data = {'lexeme_id': [], '#': [], 'english_word': []}
    for i in range(num_runs):
        data[f'ipa_run{i+1}'] = []
    
    for audio_path in audio_files:
        if not os.path.exists(audio_path):
            continue
        lexeme_id = os.path.basename(audio_path).replace('.wav', '')
        num = lexeme_id.split('_')[-1] if '_' in lexeme_id else ''
        metadata = get_metadata(audio_path)
        english_word = metadata.get('title', '').title() if metadata.get('title') else ''
        
        data['lexeme_id'].append(lexeme_id)
        data['#'].append(num)
        data['english_word'].append(english_word)
        for i in range(num_runs):
            data[f'ipa_run{i+1}'].append(all_runs[i][audio_files.index(audio_path)])
    
    df = pd.DataFrame(data)
    output_csv = os.path.join(dataset_dir, f"{dataset_name}_multi_ipa.csv")
    df.to_csv(output_csv, index=False)

    # Duplicate to Python global outputs
    global_outputs_dir = os.path.join(root_dir, 'Python global outputs')
    global_dataset_dir = os.path.join(global_outputs_dir, os.path.basename(dataset_dir))
    os.makedirs(global_dataset_dir, exist_ok=True)
    global_output_csv = os.path.join(global_dataset_dir, f"{dataset_name}_multi_ipa.csv")
    df.to_csv(global_output_csv, index=False)
    logging.info(f"Saved {output_csv} ({len(df)} rows, {num_runs} runs) and duplicated to {global_output_csv}")

# Process targets
for target_dir in target_dirs:
    dataset_dir = os.path.join(processed_root, target_dir)
    process_dataset_dir(dataset_dir)

logging.info("Multi-IPA complete.")
