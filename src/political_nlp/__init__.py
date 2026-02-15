"""
PoliticalNLP 2026 - Narrative Intelligence Analysis Pipeline

A modular pipeline for analyzing political narratives in Hungarian news media.
Extracts narrative frames, detects manipulation techniques, clusters narratives,
and generates intelligence briefs.
"""

__version__ = "0.1.0"

from .pipeline.rss_fetcher import fetch_articles
from .pipeline.narrative_extraction import extract_narratives
from .pipeline.manipulation_detection import detect_manipulation
from .pipeline.clustering import cluster_narratives
from .pipeline.brief_generation import generate_brief

__all__ = [
    'fetch_articles',
    'extract_narratives',
    'detect_manipulation',
    'cluster_narratives',
    'generate_brief',
]
