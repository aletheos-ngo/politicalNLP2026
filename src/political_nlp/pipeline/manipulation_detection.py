"""
Propaganda manipulation technique detection based on SemEval/SlavicNLP taxonomy.
Detects 25 persuasion techniques in political texts.
"""

import json
import time
from typing import Optional
import pandas as pd
from tqdm import tqdm

from ..utils.llm_client import LLMClient
from ..config import Config


VALID_LABELS = [
    "appeal_to_authority", "appeal_to_fear", "appeal_to_pity",
    "appeal_to_values", "appeal_to_hypocrisy", "appeal_to_time",
    "loaded_language", "name_calling_labelling",
    "guilt_by_association", "false_dilemma",
    "causal_oversimplification", "consequential_oversimplification",
    "flag_waving", "whataboutism", "straw_man",
    "red_herring", "bandwagon", "slogan", "exaggeration_minimisation",
    "obfuscation", "doubt", "conversation_killer", "questioning_reputation",
    "false_equivalence", "repetition"
]


def detect_from_article(
    article_text: str,
    llm_client: LLMClient,
    prompt_name: str = "manipulation_extractor",
    use_langfuse: bool = True,
) -> Optional[dict]:
    """
    Detect manipulation techniques in a single article.
    
    Args:
        article_text: Article text
        llm_client: LLMClient instance
        prompt_name: Langfuse prompt name
        use_langfuse: Whether to use Langfuse prompt template
        
    Returns:
        Dict with detected techniques, or None on failure
    """
    try:
        if use_langfuse and llm_client.use_langfuse:
            result = llm_client.call_with_prompt_template(
                prompt_name=prompt_name,
                variables={"input_text": article_text},
                trace_name="manipulation-detection",
                metadata={"project": "PoliticalNLP_2026"}
            )
        else:
            # Fallback to basic detection if Langfuse not available
            messages = [
                {"role": "system", "content": "You are a propaganda technique detector. Extract all manipulation techniques from the text."},
                {"role": "user", "content": f"INPUT TEXT:\n{article_text}\n\nExtract manipulation techniques as JSON with 'techniques' array."}
            ]
            result = llm_client.call_openai(
                messages=messages,
                model=Config.MANIPULATION_MODEL,
                temperature=0.0,
            )
        
        # Parse JSON
        if isinstance(result, str):
            result = result.strip()
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            result = json.loads(result)
        
        return result
    
    except Exception as e:
        print(f"Manipulation detection failed: {e}")
        return {"techniques": []}


def detect_manipulation(
    df: pd.DataFrame,
    output_column: str = "manipulation_techniques",
    article_column: str = "article",
    use_langfuse: bool = None,
    prompt_name: str = "manipulation_extractor",
    delay: float = None,
) -> pd.DataFrame:
    """
    Detect manipulation techniques in a DataFrame of articles.
    
    Args:
        df: Input DataFrame
        output_column: Name for output column
        article_column: Name of article text column
        use_langfuse: Whether to use Langfuse (autodetects if None)
        prompt_name: Langfuse prompt name
        delay: Seconds between requests
        
    Returns:
        DataFrame with manipulation techniques column
    """
    delay = delay if delay is not None else Config.REQUEST_DELAY
    llm_client = LLMClient(use_langfuse=use_langfuse)
    
    results = []
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Detecting manipulation"):
        article_text = row[article_column]
        
        techniques = detect_from_article(
            article_text=article_text,
            llm_client=llm_client,
            prompt_name=prompt_name,
            use_langfuse=llm_client.use_langfuse
        )
        
        results.append(techniques)
        time.sleep(delay)
    
    df[output_column] = results
    print(f"Detected manipulation for {len(df)} articles. Column: '{output_column}'")
    
    return df
