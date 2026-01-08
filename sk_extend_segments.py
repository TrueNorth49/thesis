import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

# Time parsing function
def parse_time(s):
    parts = s.strip().split(':')
    if len(parts) == 2:
        # M:SS.mmm
        m = int(parts[0])
        sec_part, ms_part = parts[1].split('.')
        sec = int(sec_part)
        ms = int(ms_part) if ms_part else 0
        total_sec = m * 60 + sec + ms / 1000
        return total_sec, 2
    elif len(parts) == 3:
        # H:M:SS.mmm
        h = int(parts[0])
        m = int(parts[1])
        sec_part, ms_part = parts[2].split('.')
        sec = int(sec_part)
        ms = int(ms_part) if ms_part else 0
        total_sec = h * 3600 + m * 60 + sec + ms / 1000
        return total_sec, 3
    else:
        raise ValueError(f"Invalid time format: {s}")

# Time formatting function
def format_time(sec, len_parts):
    if sec < 0:
        sec = 0
    if len_parts == 3:
        h = int(sec // 3600)
        sec %= 3600
        m = int(sec // 60)
        s = sec % 60
        return f"{h}:{m:02d}:{s:06.3f}"
    elif len_parts == 2:
        m = int(sec // 60)
        s = sec % 60
        return f"{m}:{s:06.3f}"
    else:
        raise ValueError("Unsupported len_parts")

# CSV loading function with encoding handling
def load_csv(csv_path):
    separators = ['\t', ',']
    encodings = ['utf-8', 'latin-1']
    for sep in separators:
        for enc in encodings:
            try:
                df = pd.read_csv(csv_path, sep=sep, engine='python', encoding=enc)
                return df
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
    raise ValueError(f"Failed to read CSV {csv_path}")

# Main function to update segments
def update_segments(csv_path):
    df = load_csv(csv_path)

    if 'Start' not in df.columns or 'Duration' not in df.columns:
        logger.warning(f"No Start/Duration columns in {csv_path}, skipping")
        return None

    # Parse times
    df['Start_sec'], df['start_fmt'] = zip(*df['Start'].apply(parse_time))
    df['Duration_sec'], df['dur_fmt'] = zip(*df['Duration'].apply(parse_time))

    # Adjust times
    df['Start_sec'] -= 0.0012  # 1.2 ms
    df['Start_sec'] = df['Start_sec'].clip(lower=0)
    df['Duration_sec'] += 0.0024  # 1.2 ms * 2

    # Format back
    df['Start'] = df.apply(lambda row: format_time(row['Start_sec'], row['start_fmt']), axis=1)
    df['Duration'] = df.apply(lambda row: format_time(row['Duration_sec'], row['dur_fmt']), axis=1)

    # Drop temp columns
    df = df.drop(['Start_sec', 'start_fmt', 'Duration_sec', 'dur_fmt'], axis=1)

    return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    folder = 'Kaso'
    if not os.path.exists(folder):
        logger.error(f"Folder {folder} not found")
        exit(1)

    files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    logger.info(f"Found {len(files)} CSV files")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)

    success_count = 0
    fail_count = 0
    for f in files:
        path = os.path.join(folder, f)
        try:
            updated_df = update_segments(path)
            if updated_df is not None:
                updated_path = path.replace('.csv', '_updated.csv')
                updated_df.to_csv(updated_path, sep='\t', index=False)

                # Duplicate to Python global outputs
                global_outputs_dir = os.path.join(root_dir, 'Python global outputs')
                global_dataset_dir = os.path.join(global_outputs_dir, folder)
                os.makedirs(global_dataset_dir, exist_ok=True)
                global_updated_path = os.path.join(global_dataset_dir, os.path.basename(updated_path))
                updated_df.to_csv(global_updated_path, sep='\t', index=False)

                success_count += 1
                logger.info(f"Updated {f} -> {updated_path} (local + Python global outputs/{folder}/{os.path.basename(updated_path)})")
            else:
                fail_count += 1
        except Exception as e:
            fail_count += 1
            logger.error(f"Failed {f}: {e}")

    logger.info(f"Summary: Processed {len(files)} files, {success_count} successful updates, {fail_count} failed/skipped")
