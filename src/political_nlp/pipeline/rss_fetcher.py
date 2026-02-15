"""
RSS feed fetching and article extraction.
Downloads news articles from Hungarian media RSS feeds.
"""

import time
from datetime import datetime, UTC
from typing import List, Set, Optional
import feedparser
from newspaper import Article
import pandas as pd
from tqdm import tqdm

from ..config import Config
from ..utils.data_io import load_existing_links


def fetch_articles(
    feed_urls: Optional[List[str]] = None,
    seen_links: Optional[Set[str]] = None,
    request_delay: float = None,
    output_file: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch articles from RSS feeds using newspaper4k for content extraction.
    
    Args:
        feed_urls: List of RSS feed URLs. If None, uses Config.RSS_FEEDS.
        seen_links: Set of already-seen article URLs to skip. If None, loads from existing parquets.
        request_delay: Seconds to wait between article fetches. If None, uses Config.REQUEST_DELAY.
        output_file: Optional filename to save results. If None, auto-generates.
        
    Returns:
        DataFrame with columns: resource, link, publication_timestamp, article
    """
    feed_urls = feed_urls or Config.RSS_FEEDS
    request_delay = request_delay if request_delay is not None else Config.REQUEST_DELAY
    
    # Load already-seen links if not provided
    if seen_links is None:
        seen_links = load_existing_links("*.parquet")
        print(f"Loaded {len(seen_links)} known article links")
    
    # Storage for results
    data = []
    
    # Fetch from each feed
    for feed_url in tqdm(feed_urls, desc="RSS feeds"):
        try:
            feed = feedparser.parse(feed_url)
            resource = feed.feed.get("title", feed_url)
            
            for entry in tqdm(feed.entries, desc=f"{resource[:30]}", leave=False):
                article_url = entry.get("link")
                if not article_url or article_url in seen_links:
                    continue
                
                # Extract publication timestamp from RSS
                pub_ts = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_ts = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    pub_ts = datetime(*entry.updated_parsed[:6])
                
                # Download and parse article
                try:
                    article = Article(article_url)
                    article.download()
                    article.parse()
                    text = article.text
                    
                    if text:
                        data.append({
                            "resource": resource,
                            "link": article_url,
                            "publication_timestamp": pub_ts,
                            "article": text
                        })
                        seen_links.add(article_url)  # Prevent duplicates within this run
                    
                except Exception as e:
                    print(f"Failed to fetch {article_url}: {str(e)}")
                    continue
                
                # Rate limiting
                time.sleep(request_delay)
        
        except Exception as e:
            print(f"Failed to parse feed {feed_url}: {str(e)}")
            continue
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
   
    print(f"Fetched {len(df)} new articles from {len(feed_urls)} feeds")
    
    # Save if requested
    if output_file:
        df.to_parquet(output_file)
        print(f"Saved to {output_file}")
    elif len(df) > 0:
        # Auto-generate filename
        run_date = datetime.now(UTC).strftime("%Y-%m-%dT%H_%M_%S")
        auto_file = f"{run_date}_data.parquet"
        df.to_parquet(auto_file)
        print(f"Saved to {auto_file}")
    
    return df
