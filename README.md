# politicalNLP2026

**Narrative Intelligence Analysis Pipeline for Hungarian Political Media**

A modular Python pipeline for extracting narrative frames from news articles, detecting propaganda manipulation techniques, clustering narratives semantically, and generating intelligence briefs. Built for academic research on political communication.

## Features

- **RSS Feed Monitoring**: Automated collection from 20+ Hungarian news sources
- **Narrative Frame Extraction**: NPF-based (Narrative Policy Framework) extraction using LLMs
- **Manipulation Detection**: 25-technique propaganda taxonomy (based on SemEval/SlavicNLP)
- **Semantic Clustering**: UMAP + HDBSCAN clustering of narrative frames
- **Intelligence Briefs**: Auto-generated markdown reports with narrative analysis
- **Langfuse Integration**: Full LLM call tracking, evaluation, and prompt management

## Installation

### Prerequisites

- Python 3.9+
- OpenAI API key (for GPT-4o) or OpenRouter/Anthropic API keys
- (Optional) Langfuse account for tracking and evaluation

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/politicalNLP2026.git
cd politicalNLP2026
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=sk-your-key-here
# LANGFUSE_PUBLIC_KEY=pk-your-key-here
# LANGFUSE_SECRET_KEY=sk-your-key-here
```

> **⚠️ IMPORTANT**: Never commit your `.env` file to git! It contains sensitive API keys.

## Quick Start

### Run the Full Pipeline

```python
from src.political_nlp.main import run_full_pipeline

# Run complete pipeline (fetch → narratives → manipulation → clustering → brief)
results = run_full_pipeline(
    output_dir="output",
    fetch_limit=10  # Limit to 10 articles for testing
)

print(f"Analyzed {results['articles_fetched']} articles")
print(f"Found {results['clusters_found']} narrative clusters")
print(f"Brief: {results['brief_generated']}")
```

### Run Individual Steps

```python
from src.political_nlp import (
    fetch_articles,
    extract_narratives,
    detect_manipulation,
    cluster_narratives,
    generate_brief
)

# 1. Fetch articles from RSS feeds
df = fetch_articles(output_file="articles.parquet")

# 2. Extract narrative frames
df = extract_narratives(df)

# 3. Detect manipulation techniques
df = detect_manipulation(df)

# 4. Cluster narratives
cluster_df = cluster_narratives(df)

# 5. Generate intelligence brief
generate_brief(cluster_df, output_file="brief.md")
```

## Pipeline Architecture

```
┌─────────────────┐
│  RSS Feeds      │ ─── 24+ Hungarian news sources
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Step 1: Article Fetching           │
│  (newspaper4k, feedparser)           │
└────────┬────────────────────────────┘
         │ articles.parquet
         ▼
┌─────────────────────────────────────┐
│  Step 2: Narrative Frame Extraction │
│  (GPT-4o, NPF schema, Langfuse)     │
└────────┬────────────────────────────┘
         │ with_narratives.parquet
         ▼
┌─────────────────────────────────────┐
│  Step 3: Manipulation Detection     │
│  (GPT-4o, 25-technique taxonomy)    │
└────────┬────────────────────────────┘
         │ with_manipulation.parquet
         ▼
┌─────────────────────────────────────┐
│  Step 4: Semantic Clustering        │
│  (sentence-transformers, HDBSCAN)   │
└────────┬────────────────────────────┘
         │ clustered_frames.parquet
         ▼
┌─────────────────────────────────────┐
│  Step 5: Intelligence Brief         │
│  (Markdown report generation)        │
└─────────────────────────────────────┘
         │ intelligence_brief.md
```

## Configuration

### Environment Variables

All sensitive configuration is loaded from `.env`:

```env
# Required: LLM API Keys
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-...        # Alternative to OpenAI
ANTHROPIC_API_KEY=sk-ant-...      # For Claude models

# Optional: Langfuse Tracking
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com

# Model Selection
NARRATIVE_MODEL=gpt-4o
MANIPULATION_MODEL=gpt-4o
BRIEF_MODEL=claude-3-5-sonnet-20241022
EMBEDDING_MODEL=paraphrase-multilingual-mpnet-base-v2

# Rate Limiting
REQUEST_DELAY=2.0                 # Seconds between API calls

# Clustering Parameters
MIN_CLUSTER_SIZE=15
MIN_SAMPLES=5
```

## Project Structure

```
politicalNLP2026/
├── src/
│   └── political_nlp/
│       ├── __init__.py           # Package exports
│       ├── config.py              # Configuration management
│       ├── main.py                # Pipeline orchestrator
│       ├── utils/
│       │   ├── llm_client.py      # Unified LLM wrapper
│       │   └── data_io.py         # DataFrame utilities
│       └── pipeline/
│           ├── rss_fetcher.py               # Article collection
│           ├── narrative_extraction.py      # NPF frame extraction
│           ├── manipulation_detection.py    # Propaganda techniques
│           ├── clustering.py                # HDBSCAN clustering
│           └── brief_generation.py          # Report generation
├── data/                         # Data files (gitignored)
├── output/                       # Pipeline outputs (gitignored)
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
└── README.md                     # This file
```

## Methodology

### Narrative Frame Extraction (NPF)

Based on the **Narrative Policy Framework** (Jones & McBeth, 2010), we extract atomic narrative elements:

- **Actors** and their portrayed roles (hero/villain/victim)
- **Actions** and claims
- **Targets** and their roles
- **Causal claims** (threat/prevention/justification logic)
- **Normative directions** (obligations, prohibitions, calls to action)
- **Constructed audiences** (in-groups, "we" references)

### Manipulation Technique Taxonomy

25 propaganda techniques from SemEval/SlavicNLP framework:

- **Emotional Appeals**: appeal_to_authority, appeal_to_fear, appeal_to_pity, appeal_to_values, appeal_to_time
- **Logical Fallacies**: false_dilemma, causal_oversimplification, consequential_oversimplification, straw_man, red_herring
- **Rhetorical Devices**: loaded_language, name_calling_labelling, slogan, flag_waving, exaggeration_minimisation
- **Distraction**: whataboutism, obfuscation, conversation_killer
- **Social Proof**: bandwagon, guilt_by_association
- **Character Attacks**: questioning_reputation, doubt
- **Others**: appeal_to_hypocrisy, false_equivalence, repetition

## Advanced Usage

### Custom RSS Feeds

```python
from src.political_nlp import fetch_articles

custom_feeds = [
    "https://example.com/rss",
    "https://another-site.com/feed"
]

df = fetch_articles(feed_urls=custom_feeds)
```

### Skip Pipeline Steps

```python
from src.political_nlp.main import run_full_pipeline

# Start from existing data, skip fetching
results = run_full_pipeline(
    input_file="data/articles.parquet",
    skip_steps=['fetch']
)
```

### Custom Clustering Parameters

```python
from src.political_nlp import cluster_narratives

cluster_df = cluster_narratives(
    df,
    min_cluster_size=20,      # Larger clusters
    min_samples=10,
    embedding_model='paraphrase-multilingual-MiniLM-L12-v2'  # Faster model
)
```

## Security & Best Practices

### API Key Security

- **Never commit API keys** to version control
- Use `.env` for all sensitive configuration
- `.gitignore` already excludes `.env` files
- Rotate keys if accidentally exposed

### Data Privacy

- Large `.parquet` files are gitignored
- Add `data/` to `.gitignore` if storing sensitive articles
- Be mindful of news article copyright when sharing datasets

## Citation

If you use this pipeline in academic research, please cite:

```bibtex
@software{politicalNLP2026,
  title={PoliticalNLP 2026: Narrative Intelligence Analysis Pipeline},
  author={Your Name},
  year={2026},
  url={https://github.com/yourusername/politicalNLP2026}
}
```

## License

[Add your license here]

## Acknowledgments

- **Narrative Policy Framework**: Jones & McBeth (2010)
- **SemEval Propaganda Detection**: Da San Martino et al. (2020)
- **Tools**: Langfuse, sentence-transformers, HDBSCAN, newspaper4k

## Support

For issues, questions, or contributions, please open an issue on GitHub.