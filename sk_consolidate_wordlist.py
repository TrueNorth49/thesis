import os
import re
import logging
import pandas as pd
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Set

load_dotenv()

def load_mapping(csv_path: str) -> Tuple[Dict[str, str], Dict[str, str], Set[str]]:
    """Load JBIL mapping from consolidated list.csv: mapping (lexical->ids_str), reverse (id->lexical), valid_ids set."""
    mapping: Dict[str, str] = {}
    reverse_mapping: Dict[str, str] = {}
    valid_ids: Set[str] = set()
    df = pd.read_csv(csv_path, sep=r'[\t|]', engine='python', header=None, skiprows=lambda x: x < 10)
    for _, row in df.iterrows():
        if len(row) >= 2:
            lexical = str(row[0]).strip().lower()
            ids_str = str(row[1]).strip()
            if lexical.isalpha() and ids_str:
                mapping[lexical] = ids_str
                for id_str_raw in ids_str.split(','):
                    id_str = id_str_raw.strip()
                    if id_str.isdigit():
                        valid_ids.add(id_str)
                        if id_str not in reverse_mapping:
                            reverse_mapping[id_str] = lexical
    logging.info(f"Parsed {len(mapping)} lexical items -> {len(valid_ids)} unique IDs")
    return mapping, reverse_mapping, valid_ids

def parse_concept_id(lexeme_id: str) -> str:
    """Parse ID from lexeme_id: base parts[1] int str, append .parts[2] if digit <=2 chars"""
    parts = lexeme_id.split('_')
    if len(parts) < 2:
        return ''
    base = str(int(parts[1].lstrip('0')) or '0')
    if len(parts) > 2 and parts[2].isdigit() and len(parts[2]) <= 2:
        sub = parts[2].lstrip('0') or '0'
        return f"{base}.{sub}"
    return base

# get_valid_ids integrated into load_mapping

def process_csv(csv_path: str, valid_ids: Set[str], reverse_mapping: Dict[str, str]) -> List[Tuple[str, str, str, str]]:
    df = pd.read_csv(csv_path)
    if df.empty:
        return []

    dataset_code = df['dataset_code'].iloc[0].title()
    kurdish_variety = df['kurdish_variety'].iloc[0]
    doculect = f"{dataset_code}_{kurdish_variety}"

    valid_rows = []
    total = len(df)
    matched = 0
    unmatched_ids = set()

    for _, row in df.iterrows():
        lexeme_id = row.get('lexeme_id', '')
        ipa_raw = row.get('ipa_transcription', '')
        if pd.isna(ipa_raw) or not ipa_raw.strip():
            continue
        ipa = re.sub(r'\s+', '', ipa_raw.strip())

        concept_id = parse_concept_id(lexeme_id)
        if concept_id in valid_ids:
            lexical_item = reverse_mapping.get(concept_id, 'UNKNOWN')
            valid_rows.append((doculect, concept_id, lexical_item, ipa))
            matched += 1
        else:
            unmatched_ids.add(concept_id)

    logging.info(f"CSV {os.path.basename(csv_path)}: {total} rows, {matched} matched")
    if unmatched_ids:
        logging.debug(f"Unmatched IDs sample: {list(unmatched_ids)[:5]}")
    return valid_rows


def run_checks(df: pd.DataFrame, valid_ids: Set[str]) -> None:
    """Post-generation checks: global + per-DOCULECT duplicates, coverage, extras. Save to wordlist_check.txt"""
    logging.info("Running consolidation checks...")

    # Global summary
    global_present = set(df['CONCEPT'].dropna().unique())
    global_dups = df.groupby('CONCEPT')['IPA'].apply(list).to_dict()
    global_dups_detail = {cid: ips for cid, ips in global_dups.items() if len(ips) > 1}
    global_dups_str = '\n'.join([f"  {cid}: {ips}" for cid, ips in global_dups_detail.items()]) if global_dups_detail else "  None"
    global_missing = sorted(valid_ids - global_present)
    global_extras = sorted(global_present - valid_ids)
    global_missing_str = ', '.join(global_missing) if global_missing else "None"
    global_extras_str = ', '.join(global_extras) if global_extras else "None"

    check_content = f"""Wordlist Check Summary (by sk_consolidate_wordlist.py):

Global:
- Total rows: {len(df)}
- Unique CONCEPTs: {len(global_present)}

Duplicates (CONCEPT -> IPA variants):
{global_dups_str}

Missing essential IDs:
{global_missing_str}

Unwanted extra IDs:
{global_extras_str}

"""

    # Per-DOCULECT
    for doculect in sorted(df['DOCULECT'].unique()):
        sub_df = df[df['DOCULECT'] == doculect]
        sub_rows = len(sub_df)
        sub_concepts = set(sub_df['CONCEPT'].dropna().unique())
        sub_dups = sub_df.groupby('CONCEPT')['IPA'].apply(list).to_dict()
        sub_dups_detail = {cid: ips for cid, ips in sub_dups.items() if len(ips) > 1}
        sub_dups_str = '\n'.join([f"  {cid}: {ips}" for cid, ips in sub_dups_detail.items()]) if sub_dups_detail else "  None"
        sub_missing = sorted(valid_ids - sub_concepts)
        sub_extras = sorted(sub_concepts - valid_ids)
        sub_missing_str = ', '.join(sub_missing) if sub_missing else "None"
        sub_extras_str = ', '.join(sub_extras) if sub_extras else "None"

        check_content += f"""## {doculect}
Total rows: {sub_rows}
Unique CONCEPTs: {len(sub_concepts)}

Duplicates:
{sub_dups_str}

Missing:
{sub_missing_str}

Extras:
{sub_extras_str}

"""

        logging.info(f"{doculect}: {sub_rows} rows, {len(sub_dups_detail)} dups, {len(sub_missing)} missing, {len(sub_extras)} extras")

    check_path = 'wordlist_check.txt'
    with open(check_path, 'w', encoding='utf-8') as f:
        f.write(check_content)
    logging.info(f"Checks saved to {check_path}")


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    audio_root = os.path.join(root_dir, 'Audio_Processed')
    csv_path = os.path.join(root_dir, 'consolidated list.csv')
    mapping, reverse_mapping, valid_ids = load_mapping(csv_path)
    logging.info(f"Using audio_root: {audio_root}")
    logging.info(f"Valid IDs count: {len(valid_ids)} from {len(mapping)} concepts")

    all_rows = []
    for subdir, _, files in os.walk(audio_root):
        for file in files:
            if file.endswith('_ipa_transcriptions.csv'):
                ipa_csv_path = os.path.join(subdir, file)
                logging.info(f"Processing: {ipa_csv_path}")
                rows = process_csv(ipa_csv_path, valid_ids, reverse_mapping)
                all_rows.extend(rows)

    if not all_rows:
        logging.warning("No valid rows!")
        return

    df = pd.DataFrame(all_rows, columns=['DOCULECT', 'CONCEPT', 'LEXICAL_ITEM', 'IPA'])
    df = df.sort_values('CONCEPT').reset_index(drop=True)
    df.insert(0, 'ID', range(1, len(df) + 1))

    output = 'wordlist.tsv'
    df.to_csv(output, sep='\t', index=False)

    # Duplicate to Python global outputs
    global_outputs_dir = os.path.join(root_dir, 'Python global outputs')
    os.makedirs(global_outputs_dir, exist_ok=True)
    global_output = os.path.join(global_outputs_dir, output)
    df.to_csv(global_output, sep='\t', index=False)
    logging.info(f"Saved {len(df)} rows to {output} and duplicated to {global_output}")

    run_checks(df, valid_ids)

    # Duplicate wordlist_check.txt
    check_path = 'wordlist_check.txt'
    global_check_path = os.path.join(global_outputs_dir, 'wordlist_check.txt')
    with open(global_check_path, 'r', encoding='utf-8') as src, open(check_path, 'r', encoding='utf-8') as dst:
        content = src.read()
        dst.write(content)
    logging.info(f"Duplicated {check_path} to {global_check_path}")

if __name__ == '__main__':
    main()
