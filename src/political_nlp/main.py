from pathlib import Path
from typing import Optional, List
import pandas as pd

from ..config import Config
from . import (
    rss_fetcher,
    narrative_extraction,
    manipulation_detection,
    clustering,
    brief_generation
)
from ..utils.data_io import merge_and_deduplicate_parquets


def run_full_pipeline(
    rss_feeds: Optional[List[str]] = None,
    input_file: Optional[str] = None,
    output_dir: str = "output",
    skip_steps: Optional[List[str]] = None,
    fetch_limit: Optional[int] = None,
) -> dict:
    """
    Run the complete PoliticalNLP analysis pipeline.
    
    Args:
        rss_feeds: List of RSS feed URLs (uses Config.RSS_FEEDS if None)
        input_file: Optional parquet file to start from (skips fetching)
        output_dir: Output directory for results
        skip_steps: List of steps to skip ('fetch', 'narratives', 'manipulation', 'clustering', 'brief')
        fetch_limit: Maximum articles to fetch (for testing)
        
    Returns:
        Dict with paths to output files and statistics
    """
    skip_steps = skip_steps or []
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = {}
    
    # Step 1: Fetch articles
    if 'fetch' not in skip_steps and not input_file:
        print("\n=== Step 1: Fetching articles ===")
        df = rss_fetcher.fetch_articles(
            feed_urls=rss_feeds,
            output_file=str(output_path / "articles.parquet")
        )
        results['articles_fetched'] = len(df)
    elif input_file:
        print(f"\n=== Loading articles from {input_file} ===")
        df = pd.read_parquet(input_file)
        results['articles_loaded'] = len(df)
    else:
        df = merge_and_deduplicate_parquets()
        results['articles_merged'] = len(df)
    
    if fetch_limit and len(df) > fetch_limit:
        print(f"Limiting to {fetch_limit} articles for testing")
        df = df.head(fetch_limit)
    
    # Step 2: Extract narrative frames
    if 'narratives' not in skip_steps:
        print("\n=== Step 2: Extracting narrative frames ===")
        df = narrative_extraction.extract_narratives(df)
        df.to_parquet(output_path / "with_narratives.parquet")
        results['narratives_extracted'] = len(df)
    
    # Step 3: Detect manipulation techniques
    if 'manipulation' not in skip_steps:
        print("\n=== Step 3: Detecting manipulation techniques ===")
        df = manipulation_detection.detect_manipulation(df)
        df.to_parquet(output_path / "with_manipulation.parquet")
        results['manipulation_detected'] = len(df)
    
    # Step 4: Cluster narratives
    if 'clustering' not in skip_steps:
        print("\n=== Step 4: Clustering narratives ===")
        cluster_df = clustering.cluster_narratives(df)
        cluster_df.to_parquet(output_path / "clustered_frames.parquet")
        results['frames_clustered'] = len(cluster_df)
        results['clusters_found'] = len(cluster_df['cluster_id'].unique()) - (1 if -1 in cluster_df['cluster_id'].values else 0)
    else:
        cluster_df = None
    
    # Step 5: Generate brief
    if 'brief' not in skip_steps and cluster_df is not None:
        print("\n=== Step 5: Generating intelligence brief ===")
        brief_path = output_path / "intelligence_brief.md"
        brief_generation.generate_brief(cluster_df, output_file=str(brief_path))
        results['brief_generated'] = str(brief_path)
    
    print("\n=== Pipeline Complete ===")
    print(f"Results saved to: {output_dir}")
    
    return results
