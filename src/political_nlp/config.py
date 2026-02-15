"""
Configuration management for PoliticalNLP pipeline.
Loads settings from environment variables and config files.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration for the PoliticalNLP pipeline."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENROUTER_API_KEY: str = os.getenv('OPENROUTER_API_KEY', '')
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Langfuse tracking (optional)
    LANGFUSE_PUBLIC_KEY: str = os.getenv('LANGFUSE_PUBLIC_KEY', '')
    LANGFUSE_SECRET_KEY: str = os.getenv('LANGFUSE_SECRET_KEY', '')
    LANGFUSE_HOST: str = os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
    
    # Model configuration
    NARRATIVE_MODEL: str = os.getenv('NARRATIVE_MODEL', 'gpt-4o')
    MANIPULATION_MODEL: str = os.getenv('MANIPULATION_MODEL', 'gpt-4o')
    BRIEF_MODEL: str = os.getenv('BRIEF_MODEL', 'claude-3-5-sonnet-20241022')
    EMBEDDING_MODEL: str = os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-mpnet-base-v2')
    
    # Rate limiting
    REQUEST_DELAY: float = float(os.getenv('REQUEST_DELAY', '2.0'))  # seconds between requests
    
    # Clustering parameters
    MIN_CLUSTER_SIZE: int = int(os.getenv('MIN_CLUSTER_SIZE', '15'))
    MIN_SAMPLES: int = int(os.getenv('MIN_SAMPLES', '5'))
    
    # RSS Feed URLs
    RSS_FEEDS: List[str] = [
        "https://telex.hu/rss",
        "https://index.hu/24ora/rss/",
        "https://24.hu/feed/",
        "https://444.hu/feed",
        "https://hvg.hu/rss",
        "https://nepszava.hu/feed",
        "https://magyarnemzet.hu/feed",
        "https://magyarhirlap.hu/rss",
        "https://mandiner.hu/rss",
        "https://pestisracok.hu/publicapi/hu/rss/pesti_sracok/articles",
        "https://www.atv.hu/feed/",
        "https://hirado.hu/hirado.aspx",
        "https://www.portfolio.hu/rss/all.xml",
        "https://merce.hu/feed/",
        "https://atlatszo.hu/feed",
        "https://www.direkt36.hu/feed/",
        "https://www.valaszonline.hu/feed",
        "https://hang.hu/rss",
        "https://168.hu/rss",
        "https://magyarnarancs.hu/rss",
        "https://demokrata.hu/feed/",
        "https://www.hirstart.hu/site/publicrss.php?pos=balrovat&pid=441",
        "https://www.hirstart.hu/site/publicrss.php?pos=toplista&pid=441",
        "https://www.hirstart.hu/site/publicrss.php?pos=vezeto&pid=74",
    ]
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY and not cls.OPENROUTER_API_KEY:
            raise ValueError(
                "No API key found. Please set OPENAI_API_KEY or OPENROUTER_API_KEY "
                "in your .env file. Copy .env.example to .env and fill in your keys."
            )
    
    @classmethod
    def use_langfuse(cls) -> bool:
        """Check if Langfuse tracking is configured."""
        return bool(cls.LANGFUSE_PUBLIC_KEY and cls.LANGFUSE_SECRET_KEY)


# Validate configuration on import
Config.validate()
