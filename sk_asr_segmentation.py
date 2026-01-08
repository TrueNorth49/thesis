#!/usr/bin/env python3
#%% Audio Segmentation - Batch Processor
# Loops through Audio_Original/*process* subdirs.
# Mirrors to Audio_Processed/<process_dir>/segments/, generates full segments (no full WAV copy).
# Derives dataset name (strip 'process'), embeds uppercase RIFF metadata via FFmpeg.
# Generates mapping.csv and metadata.csv per dataset.
# Standalone, no other scripts needed. Adheres to .clinerules.

import os
import pandas as pd
import subprocess
import re
import logging
from dotenv import load_dotenv
from typing import List, Dict

# Setup logging per .clinerules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main() -> None:
    # Robust project root detection
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    audio_original_dir = os.getenv('AUDIO_ORIGINAL_DIR', os.path.join(project_root, 'Audio_Original'))
    audio_processed_dir = os.getenv('AUDIO_PROCESSED_DIR', os.path.join(project_root, 'Audio_Processed'))
    
    # Load global .env from project root
    global_env = os.path.join(project_root, '.env')
    if os.path.exists(global_env):
        load_dotenv(global_env)
    
    # Default metadata (overridden by dataset .env / WAV parse)
    defaults = {
        'SK_VARIETY': 'SK',
        'SK_GENDER': 'M',
        'SK_AGE': '30',
        'SK_RECORD_DATE': '1990-01-01',
        'SK_EDUCATION': 'MA',
        'SK_CITY_ORIGIN': 'Toronto',
        'SK_SUBJECT': 'Spoken word',
        'SK_RESEARCHER': 'Researcher Name'
    }
    for key, default in defaults.items():
        if not os.getenv(key):
            os.environ[key] = default
    
    logger.info("Starting batch segmentation for Audio_Original/*process* dirs.")
    
    if not os.path.exists(audio_original_dir):
        raise ValueError(f"Audio_Original dir not found: {audio_original_dir}")
    
    process_dirs = [
        d for d in os.listdir(audio_original_dir)
        if os.path.isdir(os.path.join(audio_original_dir, d)) and 'process' in d.lower()
    ]
    
    if not process_dirs:
        logger.info(f"No dirs with 'process' in {audio_original_dir}")
        return
    
    total_segments = 0
    for process_dir in process_dirs:
        dataset = re.sub(r'[\s_]?process.*$', '', process_dir, flags=re.IGNORECASE).strip()
        source_dir = os.path.join(audio_original_dir, process_dir)
        
        if not os.path.exists(source_dir):
            logger.warning(f"Source dir missing: {source_dir} (for {process_dir}), skipping")
            continue
        
        processed_path = os.path.join(audio_processed_dir, process_dir)
        
        # Load dataset-specific .env (overrides globals)
        dataset_env = os.path.join(source_dir, '.env')
        if os.path.exists(dataset_env):
            load_dotenv(dataset_env, override=True)
            logger.info(f"Loaded dataset .env: {dataset_env}")
        
        # Find WAVs
        wav_files = [f for f in os.listdir(source_dir) if f.endswith('.wav')]
        if not wav_files:
            logger.warning(f"No .wav files in {source_dir}, skipping")
            continue
        
        logger.info(f"Processing {process_dir} (dataset: {dataset}), {len(wav_files)} WAVs")
        
        # Ensure dirs
        segments_folder = os.path.join(processed_path, 'segments')
        os.makedirs(segments_folder, exist_ok=True)
        
        mapping_csv = os.path.join(processed_path, 'mapping.csv')
        metadata_csv = os.path.join(processed_path, 'metadata.csv')
        
        # Process segments
        all_df = pd.DataFrame()
        all_results: List[Dict[str, str]] = []
        
        for wav_file in wav_files:
            base_name = wav_file.replace('.wav', '')
            candidates = [
                base_name,
                re.sub(r'_0\d+(?:_\w+)?$', '', base_name)
            ]
            csv_path = None
            for cand in candidates:
                candidate_csv = f"{cand}.csv"
                temp_path = os.path.join(source_dir, candidate_csv)
                if os.path.exists(temp_path):
                    csv_path = temp_path
                    logger.info(f"Matched CSV: {os.path.basename(candidate_csv)} for {wav_file}")
                    break
            
            if csv_path is None:
                logger.warning(f"No matching CSV for {wav_file} (tried {candidates}), skipping")
                continue
            
            try:
                df = pd.read_csv(csv_path, sep='\t')
            except Exception as e:
                logger.error(f"Failed to read {csv_path}: {e}")
                continue
            
            required_cols = ['Start', 'Duration']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Missing columns {required_cols} in {csv_path}")
                continue
            
            if 'Name' not in df.columns:
                logger.error(f"No 'Name' column in {csv_path}")
                continue
            
            df['audio_file'] = wav_file
            
            # Source assignment
            df['source'] = df['Name'].apply(lambda x: 'KLQ' if '(' in x or ')' in x else 'JBIL')
            
            # Parse/sort ID
            def parse_id(name: str) -> float:
                match = re.search(r'[\[(]?(\d+(?:\.\d+)?)[\])]?', name)
                return float(match.group(1)) if match else float('inf')
            
            df['id_num'] = df['Name'].apply(parse_id)
            df = df.sort_values('id_num').reset_index(drop=True)
            
            # FULL processing - no head(10)
            
            # Parse gender/age from WAV name
            sk_gender = 'F' if '_F_' in wav_file else os.getenv('SK_GENDER', 'M')
            age_match = re.search(r'_(\d{4})_', wav_file)
            sk_age = age_match.group(1) if age_match else os.getenv('SK_AGE', '30')
            
            results = []
            for idx, row in df.iterrows():
                input_file = os.path.join(source_dir, row['audio_file'])
                start = row['Start']
                duration = row['Duration']
                
                source_prefix = row['source'] + '_'
                id_int = int(row['id_num'])
                id_dec = f"_{int((row['id_num'] - id_int) * 10)}" if row['id_num'] % 1 != 0 else ''
                padded_id = str(id_int).zfill(3) + id_dec
                
                desc = re.sub(r'[\[(]?(\d+(?:\.\d+)?)[\])]?[- ]*', '', row['Name']).strip()
                clean_desc = re.sub(r'[^\w\s-]', '', desc).replace(' ', '_').lower()
                
                lexeme_id = f"{source_prefix}{padded_id}_{clean_desc}_{dataset}.wav"
                output_file = os.path.join(segments_folder, lexeme_id)
                
                # Metadata from env/WAV
                title_str = f"{source_prefix}{padded_id}_{clean_desc}_{dataset}"
                album_str = os.getenv('SK_VARIETY', 'SK')
                artist_str = f"{sk_gender}_{sk_age}"
                comment_str = f"{os.getenv('SK_EDUCATION', 'MA')}_{dataset}"
                date_str = os.getenv('SK_RECORD_DATE', '1990-01-01')
                subject_str = os.getenv('SK_SUBJECT', 'Spoken word')
                researcher_str = os.getenv('SK_RESEARCHER', 'Researcher Name')
                
                cmd = [
                    'ffmpeg', '-i', input_file,
                    '-ss', str(start), '-t', str(duration),
                    '-ar', '16000', '-ac', '1',
                    '-metadata', f'TITLE={title_str}',
                    '-metadata', f'ALBUM={album_str}',
                    '-metadata', f'ARTIST={artist_str}',
                    '-metadata', f'COMMENT={comment_str}',
                    '-metadata', f'DATE={date_str}',
                    '-metadata', f'ISBJ={subject_str}',
                    '-metadata', f'ISRC={researcher_str}',
                    '-y', output_file
                ]
                
                try:
                    subprocess.run(cmd, check=True, capture_output=True, text=True)
                    logger.info(f"Created: {lexeme_id}")
                    df.at[idx, 'audio_file'] = lexeme_id
                    results.append({'lexeme_id': lexeme_id, 'audio_path': output_file})
                except subprocess.CalledProcessError as e:
                    logger.error(f"FFmpeg failed for {lexeme_id}: {e}")
            
            all_df = pd.concat([all_df, df], ignore_index=True) if not all_df.empty else df
            all_results.extend(results)
            total_segments += len(results)
        
        # Save per dataset
        if not all_df.empty:
            all_df[['id_num', 'Name', 'Start', 'Duration', 'audio_file', 'source']].to_csv(mapping_csv, index=False)
            pd.DataFrame(all_results).to_csv(metadata_csv, index=False)

            # Duplicate to Python global outputs
            global_outputs_dir = os.path.join(project_root, 'Python global outputs')
            global_dataset_dir = os.path.join(global_outputs_dir, process_dir)
            os.makedirs(global_dataset_dir, exist_ok=True)
            global_mapping_csv = os.path.join(global_dataset_dir, 'mapping.csv')
            all_df[['id_num', 'Name', 'Start', 'Duration', 'audio_file', 'source']].to_csv(global_mapping_csv, index=False)
            global_metadata_csv = os.path.join(global_dataset_dir, 'metadata.csv')
            pd.DataFrame(all_results).to_csv(global_metadata_csv, index=False)
            logger.info(f"Saved mapping.csv ({len(all_df)}) and metadata.csv ({len(all_results)}) for {process_dir} (local + Python global outputs/{process_dir}/)")
    
    logger.info(f"Segmentation complete! Total segments processed: {total_segments}")

if __name__ == "__main__":
    main()
