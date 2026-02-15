"""
Data I/O utilities for loading, saving, and transforming DataFrames.
"""

import glob
from typing import List, Set, Optional
import pandas as pd
from datetime import datetime


def load_existing_links(pattern: str = "*.parquet") -> Set[str]:
    """
    Load already-seen article links from existing parquet files.
    
    Args:
        pattern: Glob pattern for parquet files
        
    Returns:
        Set of article URLs
    """
    seen_links = set()
    for parquet_file in glob.glob(pattern):
        try:
            tmp_df = pd.read_parquet(parquet_file, columns=["link"])
            if "link" in tmp_df.columns:
                seen_links.update(tmp_df["link"].dropna().astype(str).tolist())
        except Exception:
            continue
    return seen_links


def merge_and_deduplicate_parquets(
    pattern: str = "*.parquet",
    output_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Merge all parquet files matching pattern and deduplicate by link.
    
    Args:
        pattern: Glob pattern for parquet files
        output_name: Optional output filename. If None, auto-generated.
        
    Returns:
        Merged and deduplicated DataFrame
    """
    all_parquets = []
    for parquet_file in glob.glob(pattern):
        try:
            tmp_df = pd.read_parquet(parquet_file)
            # Only keep frames that have required columns
            if {"link", "publication_timestamp"}.issubset(tmp_df.columns):
                all_parquets.append(tmp_df)
        except Exception:
            continue
    
    if not all_parquets:
        raise ValueError("No valid parquet files with required columns found.")
    
    # Concatenate and deduplicate by link
    merged_df = pd.concat(all_parquets, ignore_index=True)
    merged_df = merged_df.drop_duplicates(subset="link")
    
    # Ensure timestamp is datetime
    merged_df = merged_df.dropna(subset=["publication_timestamp"])
    merged_df["publication_timestamp"] = pd.to_datetime(merged_df["publication_timestamp"], utc=True)
    
    # Generate output name if not provided
    if output_name is None:
        from_date = merged_df["publication_timestamp"].min().strftime("%Y-%m-%d")
        to_date = merged_df["publication_timestamp"].max().strftime("%Y-%m-%d")
        run_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        output_name = f"from_{from_date}_to_{to_date}_total_data_{run_date}.parquet"
    
    # Save
    merged_df.to_parquet(output_name)
    print(f"Saved merged dataset: {output_name} ({len(merged_df)} articles)")
    
    return merged_df


def parse_json_column(val):
    """
    Parse a JSON/dict column that might be stored as string.
    
    Args:
        val: Value to parse (dict, str, or None)
        
    Returns:
        Parsed dict or None
    """
    if val is None:
        return None
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            return eval(val)  # Be careful with eval in production!
        except Exception:
            return None
    return None


def extract_frames_from_articles(df: pd.DataFrame, narratives_col: str = 'narratives') -> pd.DataFrame:
    """
    Extract narrative frames from article DataFrame to frame-level DataFrame.
    Each row becomes one frame with article metadata attached.
    
    Args:
        df: Article-level DataFrame with narratives column
        narratives_col: Name of column containing narrative elements
        
    Returns:
        Frame-level DataFrame
    """
    from tqdm import tqdm
    
    all_frames = []
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Extracting frames"):
        narratives = parse_json_column(row.get(narratives_col))
        if not narratives:
            continue
        
        # Handle both dict with 'narrative_elements' key and list directly
        if isinstance(narratives, dict):
            narrative_list = narratives.get('narrative_elements', [])
        else:
            narrative_list = narratives
        
        for frame in narrative_list:
            causal = frame.get('causal_claim') or {}
            all_frames.append({
                'article_id':             idx,
                'source':                 row.get('resource', row.get('source', 'unknown')),
                'date':                   row.get('publication_timestamp'),
                'article_text':           str(row.get('article', ''))[:500],
                'actor':                  frame.get('actor'),
                'portrayed_role':         frame.get('portrayed_role'),
                'action_or_claim':        frame.get('action_or_claim'),
                'target':                 frame.get('target'),
                'portrayed_target_role':  frame.get('portrayed_target_role'),
                'narrative_function':     frame.get('narrative_function'),
                'causal_claim_text':      causal.get('text') if isinstance(causal, dict) else None,
                'causal_relation_type':   causal.get('causal_relation_type') if isinstance(causal, dict) else None,
            })
    
    frames_df = pd.DataFrame(all_frames)
    print(f"Extracted {len(frames_df)} frames from {len(df)} articles")
    return frames_df
