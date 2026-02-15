"""
Narrative frame clustering using sentence transformers, UMAP, and HDBSCAN.
Implements multiple clustering strategies for narrative intelligence analysis.
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
from tqdm import tqdm

from ..config import Config
from ..utils.data_io import extract_frames_from_articles


def frame_to_text(frame_row) -> str:
    """Convert a frame DataFrame row to text for embedding."""
    parts = []
    if pd.notna(frame_row.get('actor')):
        parts.append(f"Actor: {frame_row['actor']}")
    if pd.notna(frame_row.get('action_or_claim')):
        parts.append(f"Action: {frame_row['action_or_claim']}")
    if pd.notna(frame_row.get('target')):
        parts.append(f"Target: {frame_row['target']}")
    if pd.notna(frame_row.get('narrative_function')):
        parts.append(f"Function: {frame_row['narrative_function']}")
    
    return " | ".join(parts) if parts else "empty frame"


def cluster_narratives(
    df: pd.DataFrame,
    strategy: str = 'holistic',
    min_cluster_size: int = None,
    min_samples: int = None,
    embedding_model: str = None,
) -> pd.DataFrame:
    """
    Cluster narrative frames semantically.
    
    Args:
        df: DataFrame with narratives column
        strategy: Clustering strategy ('holistic', 'actor', 'claim')
        min_cluster_size: HDBSCAN min_cluster_size
        min_samples: HDBSCAN min_samples
        embedding_model: Sentence transformer model name
        
    Returns:
        Frame-level DataFrame with cluster assignments
    """
    min_cluster_size = min_cluster_size or Config.MIN_CLUSTER_SIZE
    min_samples = min_samples or Config.MIN_SAMPLES
    embedding_model = embedding_model or Config.EMBEDDING_MODEL
    
    print(f"=== Clustering with strategy: {strategy} ===")
    
    # Extract frames
    frames_df = extract_frames_from_articles(df)
    
    if len(frames_df) == 0:
        print("No frames to cluster!")
        return frames_df
    
    # Convert frames to text
    texts = frames_df.apply(frame_to_text, axis=1).tolist()
    
    # Generate embeddings
    print(f"Generating embeddings with {embedding_model}...")
    model = SentenceTransformer(embedding_model)
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    # Dimensionality reduction
    print("Reducing dimensions with UMAP...")
    reducer = umap.UMAP(
        n_neighbors=15,
        n_components=5,
        metric='cosine',
        random_state=42
    )
    reduced_embeddings = reducer.fit_transform(embeddings)
    
    # Clustering
    print(f"Clustering with HDBSCAN (min_size={min_cluster_size}, min_samples={min_samples})...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric='euclidean',
        cluster_selection_method='eom'
    )
    labels = clusterer.fit_predict(reduced_embeddings)
    
    # Add results
    frames_df['cluster_id'] = labels
    frames_df['embedding'] = list(embeddings)
    frames_df['reduced_embedding'] = list(reduced_embeddings)
    
    # Statistics
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    
    print(f"Found {n_clusters} clusters, {n_noise} noise points")
    print(f"Cluster sizes: {pd.Series(labels).value_counts().sort_index()}")
    
    return frames_df


def auto_label_clusters(
    frames_df: pd.DataFrame,
    cluster_column: str = 'cluster_id',
    label_column: str = 'cluster_label',
    actor_column: str = 'actor',
    claim_column: str = 'action_or_claim',
) -> pd.DataFrame:
    """
    Auto-generate cluster labels from most common actors/claims.
    
    Args:
        frames_df: Frame DataFrame
        cluster_column: Name of cluster ID column
        label_column: Name for output label column
        actor_column: Name of actor column
        claim_column: Name of claim column
        
    Returns:
        DataFrame with cluster labels added
    """
    labels_map = {}
    
    for cluster_id in frames_df[cluster_column].unique():
        if cluster_id == -1:
            labels_map[cluster_id] = "noise"
            continue
        
        cluster_frames = frames_df[frames_df[cluster_column] == cluster_id]
        
        # Get most common actor
        top_actor = cluster_frames[actor_column].value_counts().index[0] if len(cluster_frames) > 0 else "unknown"
        
        labels_map[cluster_id] = f"Cluster {cluster_id}: {top_actor[:30]}"
    
    frames_df[label_column] = frames_df[cluster_column].map(labels_map)
    
    return frames_df
