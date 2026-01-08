#%% Audio Segmentation
# This section segments the audio based on TSV timestamps and embeds metadata using standard RIFF INFO tags via FFmpeg.
# Run this to (re)generate segments with the updated metadata scheme.
# Updates: Moved hardcoded 'Halabja' to sk_city_origin from .env. Added loading of SK_SUBJECT and SK_RESEARCHER from .env, using them in metadata cmd instead of hardcoded strings.

import os
import pandas as pd
import subprocess
import re
from dotenv import load_dotenv

load_dotenv()  # Load .env from cwd

print("Script started - loading config from .env...")
print(f"cwd: {os.getcwd()}")
print(f".env exists: {os.path.exists('.env')}")

# Load paths and metadata from .env with defaults
tsv_path = os.getenv('TSV_PATH')
audio_dir = os.getenv('AUDIO_DIR')
audio_file_name = os.getenv('AUDIO_FILE_NAME')
segments_folder = os.getenv('SEGMENTS_FOLDER')
dataset_name = os.getenv('DATASET_NAME')
processed_dir = os.getenv('PROCESSED_DIR')
tsv_path_full = os.path.join(audio_dir, tsv_path)

dataset_env_path = os.path.join(audio_dir, '.env')
if os.path.exists(dataset_env_path):
    load_dotenv(dataset_env_path)

kurdish_variety = os.getenv('KURDISH_VARIETY', 'SK')
gender = os.getenv('GENDER', 'M')
dataset_code = os.getenv('DATASET_CODE', 'DatasetCode')
age = os.getenv('AGE', '30')
record_date = os.getenv('RECORD_DATE', '1990-01-01')
education = os.getenv('EDUCATION', 'MA/PhD')
city_origin = os.getenv('CITY_ORIGIN', 'Toronto')
subject = os.getenv('SUBJECT', 'Spoken word')
researcher = os.getenv('RESEARCHER', 'Researcher Name')

print(f"tsv_path: {tsv_path}")
print(f"audio_dir: {audio_dir}")
print(f"audio_file_name: {audio_file_name}")
print(f"segments_folder: {segments_folder}")
print(f"dataset_name: {dataset_name}")
print(f"processed_dir: {processed_dir}")

if tsv_path is None or audio_dir is None or audio_file_name is None or segments_folder is None or dataset_name is None or processed_dir is None:
    raise ValueError("Missing required .env variables for segmentation. Please set them in .env.")

# Create folders if not exist
os.makedirs(processed_dir, exist_ok=True)
dataset_folder = os.path.join(processed_dir, dataset_name)
os.makedirs(dataset_folder, exist_ok=True)
os.makedirs(segments_folder, exist_ok=True)
originals_folder = os.path.join(dataset_folder, 'originals')
os.makedirs(originals_folder, exist_ok=True)

input_wav_path = os.path.join(audio_dir, audio_file_name)
mapping_csv = os.path.join(dataset_folder, 'mapping.csv')
metadata_csv = os.path.join(dataset_folder, 'metadata.csv')

print(f"Using TSV_PATH: {tsv_path}")
print(f"Using INPUT_WAV_PATH: {input_wav_path}")
print(f"Using SEGMENTS_FOLDER: {segments_folder}")
print(f"Using VARIETY: {kurdish_variety}")
print(f"Using GENDER: {gender}")
print(f"Using DATASET_CODE (Speaker ID): {dataset_code}")
print(f"Using AGE: {age}")
print(f"Using RECORD_DATE: {record_date}")
print(f"Using EDUCATION: {education}")
print(f"Using CITY_ORIGIN: {city_origin}")
print(f"Using SUBJECT: {subject}")
print(f"Using RESEARCHER: {researcher}")

# Load TSV (tab-separated)
df = pd.read_csv(tsv_path_full, sep='\t')
# Test limit: First 10 rows only (remove for full run)
# df = df.head(10)
# Add audio_file if missing
if 'audio_file' not in df.columns:
    df['audio_file'] = audio_file_name
# Assign source based on parentheses
df['source'] = df['Name'].apply(lambda x: 'KLQ' if '(' in x or ')' in x else 'JBIL')
# Parse ID for sorting
def parse_id(name):
    match = re.search(r'[\[(]?(\d+(?:\.\d+)?)[\])]?', name)
    return float(match.group(1)) if match else float('inf')
df['id_num'] = df['Name'].apply(parse_id)
df = df.sort_values('id_num').reset_index(drop=True)
# Generate mapping CSV with source
df[['id_num', 'Name', 'Start', 'Duration', 'audio_file', 'source']].to_csv(mapping_csv, index=False)
print(f"Mapping CSV saved to {mapping_csv}")
# City of origin for this dataset (will concatenate into comment since no dedicated tag)
city_origin = city_origin
# Segment in sorted order
results = []
for index, row in df.iterrows():
    input_file = os.path.join(audio_dir, row['audio_file'])
    start = row['Start']
    duration = row['Duration']
   
    # New naming scheme: Source_TripleDigitQuestionNumber_LexicalItem_DatasetCode
    source_prefix = row['source'] + '_'
    # Split id_num into integer and decimal parts for padding
    id_int = int(row['id_num'])
    id_dec = f"_{int((row['id_num'] - id_int) * 10)}" if row['id_num'] % 1 != 0 else '' # e.g., .1 → _1
    padded_id = str(id_int).zfill(3) + id_dec # e.g., '001' or '001_1'
    desc = re.sub(r'[\[(]?(\d+(?:\.\d+)?)[\])]?[- ]*', '', row['Name']).strip() # Remove prefix robustly
    clean_desc = desc.replace(' ', '_').replace('?', '').replace('"', '').replace('(', '').replace(')', '').lower() # Lowercase here
    lexeme_id = f"{source_prefix}{padded_id}_{clean_desc}_{dataset_code}.wav"
    output_file = os.path.join(segments_folder, lexeme_id)
   
    # Build metadata values for Windows properties categories: Title, Subtitle, Album, Year, #, Genre
    title_str = clean_desc  # Title
    subtitle_str = f"{gender} {age} {dataset_code}"  # Subtitle
    album_str = kurdish_variety  # Album
    year_num = record_date.split('-')[0] if '-' in record_date else record_date[:4]  # Year
    track_str = f"{education} {city_origin}"  # # (track)
    genre_str = f"{researcher} {subject}"  # Genre
   
    cmd = [
        'ffmpeg', '-i', input_file,
        '-ss', start, '-t', duration,
        '-ar', '16000', '-ac', '1',
        '-metadata', f'title={title_str}',
        '-metadata', f'subtitle={subtitle_str}',
        '-metadata', f'album={album_str}',
        '-metadata', f'year={year_num}',
        '-metadata', f'track={track_str}',
        '-metadata', f'genre={genre_str}',
        '-y', output_file
    ]
    subprocess.run(cmd, check=True)
    print(f"Created: {output_file} (with metadata: Title={title_str}, Subtitle={subtitle_str}, Album={album_str}, Year={year_num}, Track={track_str}, Genre={genre_str})")
    df.at[index, 'audio_file'] = lexeme_id
    results.append({'lexeme_id': lexeme_id, 'audio_path': output_file})

# Update and save mapping CSV with audio_file
df.to_csv(mapping_csv, index=False)

# Duplicate mapping and metadata to Python global outputs
global_outputs_dir = os.path.dirname(os.path.dirname(dataset_folder))
global_dataset_dir = os.path.join(global_outputs_dir, 'Python global outputs', os.path.basename(dataset_folder))
os.makedirs(global_dataset_dir, exist_ok=True)
global_mapping_csv = os.path.join(global_dataset_dir, 'mapping.csv')
df.to_csv(global_mapping_csv, index=False)
global_metadata_csv = os.path.join(global_dataset_dir, 'metadata.csv')

# Save metadata CSV
pd.DataFrame(results).to_csv(metadata_csv, index=False)
pd.DataFrame(results).to_csv(global_metadata_csv, index=False)
print(f"Segmentation complete! Files in {dataset_folder}: mapping.csv, metadata.csv. Duplicated to Python global outputs/{os.path.basename(dataset_folder)}/")
exit()
from transformers import pipeline
import torch
import os
import pandas as pd
import subprocess
import logging
import json
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

segments_folder = os.path.normpath(os.getenv('SEGMENTS_FOLDER'))
output_csv = os.path.normpath(os.getenv('OUTPUT_CSV'))
ck_model = os.getenv('CK_MODEL', 'razhan/whisper-base-ckb')  # Updated non-gated CK model
sk_model = os.getenv('SK_MODEL', 'razhan/whisper-base-sdh')  # Default SK model
sk_processed_dir = os.path.normpath(os.getenv('SK_PROCESSED_DIR'))
sk_dataset_name = os.getenv('SK_DATASET_NAME')
sk_audio_dir = os.path.normpath(os.getenv('SK_AUDIO_DIR'))
sk_audio_file_name = os.getenv('SK_AUDIO_FILE_NAME')
sk_variety = os.getenv('SK_VARIETY', 'CK/SK')  # Default to 'CK'; determines model
sk_gender = os.getenv('SK_GENDER', 'M')
sk_dataset_code = os.getenv('SK_DATASET_CODE', 'First four characters of city + dataset')
sk_age = os.getenv('SK_AGE', '30')
sk_record_date = os.getenv('SK_RECORD_DATE', '1990-01-01')
sk_education = os.getenv('SK_EDUCATION', 'MA')
sk_city_origin = os.getenv('SK_CITY_ORIGIN', 'Toronto')
sk_subject = os.getenv('SK_SUBJECT', 'Spoken word')
sk_researcher = os.getenv('SK_RESEARCHER', 'Researcher Name')

if segments_folder is None or output_csv is None or sk_processed_dir is None or sk_dataset_name is None or sk_audio_dir is None or sk_audio_file_name is None:
    raise ValueError("Missing required .env variables for ASR: SEGMENTS_FOLDER, OUTPUT_CSV, SK_PROCESSED_DIR, SK_DATASET_NAME, SK_AUDIO_DIR, SK_AUDIO_FILE_NAME. Please set them in .env.")

metadata_csv = os.path.normpath(os.path.join(sk_processed_dir, sk_dataset_name, 'metadata.csv'))
input_wav_path = os.path.normpath(os.path.join(sk_audio_dir, sk_audio_file_name))

logging.info(f"Using SEGMENTS_FOLDER: {segments_folder}")
logging.info(f"Using METADATA_CSV: {metadata_csv}")
logging.info(f"Using OUTPUT_CSV: {output_csv}")
logging.info(f"Using INPUT_WAV_PATH for original metadata: {input_wav_path}")
logging.info(f"Using VARIETY: {sk_variety}")
logging.info(f"Selected ASR_MODEL: {ck_model if sk_variety == 'CK' else sk_model}")

device = 0 if torch.cuda.is_available() else -1
logging.info(f"Device set to use {'cuda:0' if device == 0 else 'cpu'}")

# Select model based on variety
asr_model = ck_model if sk_variety == 'CK' else sk_model
asr_pipe = pipeline("automatic-speech-recognition", model=asr_model, device=device)

def get_metadata(file_path):
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

# Extract metadata from the original audio file (shared across all segments)
original_metadata = get_metadata(input_wav_path)
logging.info(f"Original audio metadata: {original_metadata}")

# Load audio paths from metadata.csv if exists, else from segments_folder
audio_files = []
if os.path.exists(metadata_csv):
    metadata_df = pd.read_csv(metadata_csv)
    audio_files = [os.path.normpath(p) for p in metadata_df['audio_path'].tolist()][:50]
    logging.info(f"Loaded {len(audio_files)} audio paths from {metadata_csv}")
elif os.path.exists(segments_folder):
    audio_files = sorted([os.path.normpath(os.path.join(segments_folder, f)) for f in os.listdir(segments_folder) if f.endswith('.wav')])[:50]
    logging.info(f"Loaded {len(audio_files)} audio files from {segments_folder}")
else:
    raise ValueError("SEGMENTS_FOLDER or METADATA_CSV does not exist. Check .env settings.")

if not audio_files:
    raise ValueError("No audio files found. Ensure segments exist or run segmentation first.")

results = []
for idx, row in df.iterrows():
    audio_path = os.path.normpath(row['audio_path'])
    lexeme_id = row['lexeme_id']
    source = row['source']
    survey_item = row['id_num']
    speaker_id = sk_dataset_code
    name = row.get('Name', '')
    # english_word from Name (remove id prefix) or title
    english_word = re.sub(r'[\[(]?\d+(?:\.\d+)?[\])]?[- ]*', '', name).strip()
    if not english_word:
        segment_metadata = get_metadata(audio_path)
        english_word = segment_metadata.get('title', 'unknown').title()

    logging.info(f"Processing {lexeme_id}: source={source}, survey_item={survey_item}, english={english_word}")

    arabic_transcription = ''
    try:
        arabic_transcription = whisper_pipe(audio_path)['text'].strip()
    except Exception as e:
        logging.error(f"Whisper error for {audio_path}: {e}")

    arabic_transcription_sdh = ''
    try:
        arabic_transcription_sdh = sdh_pipe(audio_path)['text'].strip()
    except Exception as e:
        logging.error(f"SDH error for {audio_path}: {e}")

    ipa_transcription = ''
    try:
        ipa_transcription = ipa_pipe(audio_path)['text'].strip()
    except Exception as e:
        logging.error(f"IPA error for {audio_path}: {e}")

    segment_metadata = get_metadata(audio_path)

    results.append({
        'source': source,
        'survey_item': survey_item,
        'speaker_id': speaker_id,
        'english_word': english_word,
        'arabic_transcription': arabic_transcription,
        'arabic_transcription_sdh': arabic_transcription_sdh,
        'ipa_transcription': ipa_transcription,
        'kurdish_variety': kurdish_variety,
        'kurdish_dialect': kurdish_dialect,
        **segment_metadata
    })

df_results = pd.DataFrame(results)

# Priority columns first
priority_cols = ['source', 'survey_item', 'speaker_id', 'english_word', 'arabic_transcription', 'arabic_transcription_sdh', 'ipa_transcription', 'kurdish_variety', 'kurdish_dialect']
other_cols = [col for col in df_results.columns if col not in priority_cols]
df_results = df_results[priority_cols + other_cols]

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)

df_results.to_csv(output_csv, index=False)

# Duplicate to Python global outputs
global_outputs_dir = os.path.join(root_dir, 'Python global outputs')
global_dataset_dir = os.path.join(global_outputs_dir, sk_dataset_name)
os.makedirs(global_dataset_dir, exist_ok=True)
global_output_csv = os.path.join(global_dataset_dir, os.path.basename(output_csv))
df_results.to_csv(global_output_csv, index=False)

logging.info(f"ASR complete! Results saved to {output_csv} and duplicated to {global_output_csv}")
print(f"Output CSV saved: {output_csv} (duplicated to Python global outputs/{sk_dataset_name}/)")
