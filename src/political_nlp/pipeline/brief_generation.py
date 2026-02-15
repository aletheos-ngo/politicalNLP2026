"""
Intelligence brief generation from clustered narrative frames.
Creates markdown reports with narrative analysis and recommendations.
"""

from datetime import datetime
from typing import Optional
import pandas as pd
from ..utils.llm_client import LLMClient
from ..config import Config


def generate_brief(
    cluster_df: pd.DataFrame,
    output_file: Optional[str] = None,
    llm_client: Optional[LLMClient] = None,
) -> str:
    """
    Generate narrative intelligence brief from clustered frames.
    
    Args:
        cluster_df: DataFrame with clustered narrative frames
        output_file: Optional output markdown file path
        llm_client: Optional LLMClient for enhanced analysis
        
    Returns:
        Brief text as markdown string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    brief = f"""# Narrative Intelligence Brief
Generated: {timestamp}

## Executive Summary

Total articles analyzed: {cluster_df['article_id'].nunique()}
Total narrative frames extracted: {len(cluster_df)}
Clusters identified: {len(cluster_df['cluster_id'].unique()) - (1 if -1 in cluster_df['cluster_id'].values else 0)}

## Cluster Analysis

"""
    
    # Analyze each cluster
    for cluster_id in sorted(cluster_df['cluster_id'].unique()):
        if cluster_id == -1:
            continue
        
        cluster_frames = cluster_df[cluster_df['cluster_id'] == cluster_id]
        
        brief += f"### Cluster {cluster_id}: {cluster_frames.iloc[0].get('cluster_label', 'Unlabeled')}\n\n"
        brief += f"- **Size**: {len(cluster_frames)} frames\n"
        brief += f"- **Sources**: {cluster_frames['source'].nunique()} unique sources\n"
        brief += f"- **Date range**: {cluster_frames['date'].min()} to {cluster_frames['date'].max()}\n"
        
        # Top actors
        top_actors = cluster_frames['actor'].value_counts().head(3)
        brief += f"- **Top actors**: {', '.join(top_actors.index.tolist())}\n"
        
        # Top narrative functions
        top_functions = cluster_frames['narrative_function'].value_counts().head(3)
        brief += f"- **Narrative functions**: {', '.join(top_functions.index.tolist())}\n\n"
        
        # Sample frame
        sample = cluster_frames.iloc[0]
        brief += f"**Sample frame**:\n"
        brief += f"- Actor: {sample.get('actor', 'N/A')}\n"
        brief += f"- Action: {sample.get('action_or_claim', 'N/A')}\n"
        brief += f"- Target: {sample.get('target', 'N/A')}\n\n"
        
        brief += "---\n\n"
    
    # Save if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(brief)
        print(f"Brief saved to {output_file}")
    
    return brief
