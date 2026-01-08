# IPA Transcription Program
# This script processes audio segments to generate IPA transcriptions using the specified Hugging Face model.
# It outputs an IPA CSV and combines with the previous orthographic transcription CSV to create a new combined file.
# Adapted from sk_asr_notebook_transcription_backup.py

from transformers import pipeline
import torch
import os
import pandas as pd
import logging
import json
import subprocess
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import glob
from pathlib import Path

# Optional root .env
load_dotenv()

# Compute project root-relative path (script in scripts/)
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
processed_root = os.path.normpath(os.path.join(root_dir, 'Audio_Processed'))

if not os.path.exists(processed_root):
    raise ValueError(f"Audio_Processed directory not found at: {processed_root}")

# Discover target directories: 'process' in name, has segments/ and .env
target_dirs = [
    d for d in os.listdir(processed_root)
    if os.path.isdir(os.path.join(processed_root, d))
    and 'process' in d.lower()
    and os.path.exists(os.path.join(processed_root, d, 'segments'))
    and os.path.exists(os.path.join(processed_root, d, '.env'))
]

if not target_dirs:
    raise ValueError("No target directories found in Audio_Processed/ with 'process' in name, segments/, and .env")

logging.info(f"Found target directories: {target_dirs}")

ipa_model = 'facebook/wav2vec2-xlsr-53-espeak-cv-ft'

device = 0 if torch.cuda.is_available() else -1
logging.info(f"Device set to use {'cuda:0' if device == 0 else 'cpu'}")


def process_dataset_dir(dataset_dir: str) -> None:
    """Process a single dataset directory: generate ortho + IPA transcriptions and save combined CSV."""
    # Load per-dir .env
    load_dotenv(os.path.join(dataset_dir, '.env'))
    
    dataset_name_raw = os.getenv('DATASET_NAME', os.path.basename(dataset_dir))
    dataset_name = dataset_name_raw.lower().replace(' ', '').replace('process', '').strip()
    
    segments_folder = os.path.normpath(os.getenv('SEGMENTS_FOLDER', os.path.join(dataset_dir, 'segments')))
    metadata_csv_path = os.path.join(dataset_dir, os.getenv('METADATA_CSV', 'metadata.csv'))
    kurdish_variety = os.getenv('KURDISH_VARIETY', 'CK')
    originals_dir = os.path.join(dataset_dir, os.getenv('AUDIO_DIR', 'originals'))
    audio_file_name = os.getenv('AUDIO_FILE_NAME')
    input_wav_path = os.path.join(originals_dir, audio_file_name) if audio_file_name else None
    
    logging.info(f"Processing {dataset_dir}: dataset_name={dataset_name}, variety={kurdish_variety}, segments={segments_folder}")
    
    # Select ortho model
    ck_model = os.getenv('CK_MODEL', 'razhan/whisper-base-ckb')
    sk_model = os.getenv('SK_MODEL', 'razhan/whisper-base-sdh')
    ortho_model = ck_model if kurdish_variety.upper() == 'CK' else sk_model
    
    # Load pipelines
    ortho_pipe = pipeline("automatic-speech-recognition", model=ortho_model, device=device)
    ipa_pipe = pipeline("automatic-speech-recognition", model=ipa_model, device=device)
    
    # Load audio files (full, no limit)
    audio_files = []
    if os.path.exists(metadata_csv_path):
        metadata_df = pd.read_csv(metadata_csv_path)
        if 'audio_path' in metadata_df.columns:
            audio_files = [os.path.normpath(p) for p in metadata_df['audio_path'].tolist()]
        logging.info(f"Loaded {len(audio_files)} audio paths from {metadata_csv_path}")
    if not audio_files and os.path.exists(segments_folder):
        audio_files = sorted([
            os.path.normpath(os.path.join(segments_folder, f))
            for f in os.listdir(segments_folder)
            if f.endswith('.wav')
        ])
        logging.info(f"Loaded {len(audio_files)} audio files from {segments_folder}")
    
    if not audio_files:
        logging.warning(f"No audio files in {dataset_dir}. Skipping.")
        return
    
    # Env metadata (constant across files)
    env_metadata = {
        'kurdish_variety': kurdish_variety,
        'gender': os.getenv('GENDER'),
        'age': os.getenv('AGE'),
        'education': os.getenv('EDUCATION'),
        'city_origin': os.getenv('CITY_ORIGIN'),
        'subject': os.getenv('SUBJECT'),
        'researcher': os.getenv('RESEARCHER'),
        'record_date': os.getenv('RECORD_DATE'),
        'dataset_code': os.getenv('DATASET_CODE'),
    }
    
    # Original metadata
    original_metadata = get_metadata(input_wav_path) if input_wav_path and os.path.exists(input_wav_path) else {}
    
    # Batch process orthographic and IPA
    try:
        ortho_results = ortho_pipe(audio_files, batch_size=16)
        ortho_transcriptions = [r['text'].strip() if isinstance(r, dict) and 'text' in r and isinstance(r['text'], str) else '' for r in ortho_results]
    except Exception as e:
        logging.error(f"Batch ortho ASR error: {e}")
        ortho_transcriptions = [''] * len(audio_files)

    try:
        ipa_results = ipa_pipe(audio_files, batch_size=16)
        ipa_transcriptions = [r['text'].strip() if isinstance(r, dict) and 'text' in r and isinstance(r['text'], str) else '' for r in ipa_results]
    except Exception as e:
        logging.error(f"Batch IPA ASR error: {e}")
        ipa_transcriptions = [''] * len(audio_files)

    # Build results
    results = []
    for audio_path, ortho_trans, ipa_trans in zip(audio_files, ortho_transcriptions, ipa_transcriptions):
        if not os.path.exists(audio_path):
            logging.warning(f"Audio file missing: {audio_path}")
            continue
        
        lexeme_id = os.path.basename(audio_path).replace('.wav', '')
        segment_metadata = get_metadata(audio_path)
        
        row = {
            'lexeme_id': lexeme_id,
            'audio_path': audio_path,
            'orthographic_transcription': ortho_trans,
            'ipa_transcription': ipa_trans,
            **env_metadata,
            **segment_metadata,
            'original_metadata_json': json.dumps(original_metadata),
        }
        results.append(row)
    
    if not results:
        logging.warning(f"No results for {dataset_dir}")
        return
    
    df = pd.DataFrame(results)
    
    # Additional derived columns
    df['#'] = df['lexeme_id'].str.split('_').str[-1] if 'lexeme_id' in df else ''
    df['lexical_item_survey'] = df['lexeme_id'].str.split('_').str[0]
    
    # Select specific columns (remove subject (L), artist-P to ISRC-X)
    keep_cols = ['lexical_item_survey', '#', 'orthographic_transcription', 'ipa_transcription', 'lexeme_id', 
                 'kurdish_variety', 'gender', 'age', 'education', 'city_origin', 
                 'researcher', 'record_date', 'dataset_code', 'audio_path']
    df = df[keep_cols]
    
    # Add citation columns
    df['ortho_model'] = ortho_model
    df['ipa_model'] = ipa_model
    df['packages'] = 'ASR: transformers, torch, torchaudio, accelerate, phonemizer; Segmentation: ffmpeg-python, pandas, python-dotenv (sk_asr_segmentation.py)'
    
    # Reorder: audio_path last, then citations
    col_order = ['lexical_item_survey', '#', 'orthographic_transcription', 'ipa_transcription', 'lexeme_id', 
                 'kurdish_variety', 'gender', 'age', 'education', 'city_origin', 
                 'researcher', 'record_date', 'dataset_code', 'audio_path', 'ortho_model', 'ipa_model', 'packages']
    df = df[col_order]
    
    # Save
    output_csv = os.path.join(dataset_dir, f"{dataset_name}_ipa_transcriptions.csv")
    df.to_csv(output_csv, index=False)

    # Duplicate to Python global outputs
    global_outputs_dir = os.path.join(root_dir, 'Python global outputs')
    global_dataset_dir = os.path.join(global_outputs_dir, os.path.basename(dataset_dir))
    os.makedirs(global_dataset_dir, exist_ok=True)
    global_output_csv = os.path.join(global_dataset_dir, f"{dataset_name}_ipa_transcriptions.csv")
    df.to_csv(global_output_csv, index=False)
    logging.info(f"Saved consolidated transcriptions to {output_csv} ({len(df)} rows) and duplicated to {global_output_csv}")


def get_metadata(file_path: str) -> dict:
    """Extract metadata tags from an audio file using ffprobe."""
    file_path = os.path.normpath(file_path)
    if not os.path.exists(file_path):
        logging.warning(f"File not found for metadata extraction: {file_path}")
        return {}
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_entries', 'format_tags', file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error extracting metadata from {file_path}: {result.stderr}")
        return {}
    try:
        data = json.loads(result.stdout)
        return data.get('format', {}).get('tags', {})
    except json.JSONDecodeError:
        logging.error(f"Error parsing metadata JSON from {file_path}")
        return {}


# Process all target directories
for target_dir in target_dirs:
    dataset_dir = os.path.join(processed_root, target_dir)
    process_dataset_dir(dataset_dir)

logging.info("All datasets processed.")
