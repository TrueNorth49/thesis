#%% Metadata Check Script
# This section provides a standalone script to verify if metadata is correctly embedded in the segmented .wav files.
# It uses ffprobe to extract and print all metadata tags from all .wav files in the folder (or a sample).
# Run this in your Jupyter notebook or as a .py file to diagnose issues.
# Updates: No changes needed.

import os
import subprocess
import json
from dotenv import load_dotenv

load_dotenv()

segments_folder = os.getenv('SEGMENTS_FOLDER')
if segments_folder is None:
    raise ValueError("SEGMENTS_FOLDER not set in .env")

# Standardize path
segments_folder = os.path.normpath(segments_folder)

# Get all .wav files
wav_files = sorted([os.path.normpath(os.path.join(segments_folder, f)) for f in os.listdir(segments_folder) if f.endswith('.wav')])[:10]  # Limit to 10; remove [:10] for all
if not wav_files:
    raise ValueError("No .wav files found in SEGMENTS_FOLDER")

expected_keys = ['title', 'album', 'artist', 'comment', 'date', 'isbj', 'isrc']  # Updated to lowercase four-letter

for sample_wav in wav_files:
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_entries', 'format_tags', sample_wav
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error extracting metadata from {sample_wav}: {result.stderr}")
        continue
    try:
        data = json.loads(result.stdout)
        tags = data.get('format', {}).get('tags', {})
        print(f"Metadata for {sample_wav}:")
        for key, value in tags.items():
            print(f"{key}: {value}")
        # Check for expected keys
        missing = [k for k in expected_keys if k not in tags]
        if missing:
            print(f"Missing expected metadata keys in {sample_wav}: {', '.join(missing)}")
        # Parse and print derived values
        print("Derived metadata:")
        if 'title' in tags:
            title_parts = tags['title'].rsplit('_', 1)  # Split off last _ for dataset_code
            print(f"lexeme: {title_parts[0]}, dataset_code: {title_parts[1]}")
        print(f"variety: {tags.get('album', 'N/A')}")
        if 'artist' in tags:
            gender, age = tags['artist'].split('_')
            print(f"gender: {gender}, age: {age}")
        if 'comment' in tags:
            education, city_origin = tags['comment'].split('_')
            print(f"education: {education}, city_origin: {city_origin}")
        print(f"record_date: {tags.get('date', 'N/A')}")
        print(f"subject: {tags.get('isbj', 'N/A')}")
        print(f"researcher: {tags.get('isrc', 'N/A')}")
        print("\n")
    except json.JSONDecodeError:
        print(f"Error parsing metadata JSON from {sample_wav}")
    except ValueError as e:
        print(f"Error parsing concatenated metadata in {sample_wav}: {e}")