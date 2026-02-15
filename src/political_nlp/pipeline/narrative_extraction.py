"""
Narrative frame extraction using NPF (Narrative Policy Framework).
Extracts atomic narrative elements from Hungarian news articles.
"""

import json
import time
from typing import Optional, Union
from datetime import datetime
import pandas as pd
from tqdm import tqdm

from ..utils.llm_client import LLMClient
from ..config import Config


# Default prompts (can be overridden by Langfuse templates)
SYSTEM_PROMPT = """You are performing narrative analysis grounded in the Narrative Policy Framework (NPF).
Your task is to extract atomic narrative elements from a Hungarian news article.
These elements are analytical abstractions for narrative intelligence and escalation analysis,
not factual event logs and not moral or legal judgments."""

ANALYSIS_PROMPT = """# TASK
Extract atomic narrative elements from the article below. Follow the schema exactly. Every field is required — use null where appropriate but never omit a field.

# SCHEMA (all fields mandatory)
```json
{
  "narrative_elements": [
    {
      "actor": "exact surface form as in text",
      "actor_type": "individual | institution | group | abstract | media | unspecified",

      "speaker_role": "hero_narrator | narrator | neutral | unclear",
      // Who is the speaker performing as? If mobilising, defending, or positioning as protector → hero_narrator. If reporting → narrator. If ambiguous → unclear.

      "portrayed_role": "hero | villain | victim | narrator | neutral | unclear",
      // How does the TEXT construct this actor? Not your judgment. Must be supported by evidence_span.

      "narrative_function": "claim | evaluation | threat | mobilisation | warning | policy_promise",
      // MANDATORY. Choose ONE. See decision table below. Do NOT use background or logistics — those should not be extracted.

      "action_or_claim": "what the actor does, says, or is described as doing",

      "target": "exact surface form, or null",
      "target_type": "individual | institution | group | abstract | unspecified | null",
      "portrayed_target_role": "hero | villain | victim | threat | proxy | neutral | unclear | null",
      // threat = trigger entity that causes catastrophe; proxy = stands in for a larger villain

      "causal_claim": {
        "text": "explicit causal statement from the text, or null",
        "causal_marker_surface": "because | therefore | if | when | so_that | implied | null",
        // Use the actual logical connector. Not grammatical particles (hogy, onnan, ami are NOT causal markers unless they introduce a cause-effect).
        "causal_relation_type": "threat | prevention | retaliation | inevitability | zero_sum | justification | null"
        // What kind of causal logic? threat = X causes harm; prevention = X stops harm; justification = X explains Y.
      },

      "normative_direction": "explicit demand, prohibition, or call — or null",
      "normative_type": "prohibition | obligation | encouragement | warning | prediction | null",
      // prohibition = must NOT; obligation = must; encouragement = should/rally; warning = if not, then harm; prediction = will happen

      "constructed_audience": "explicit in-group label from the text (e.g. 'mi', 'magyarok', 'fiatalok'), or null",
      // Only if the text explicitly constructs a 'we' or addresses a defined group.

      "attribution": "direct_quote | attributed_claim | journalistic_paraphrase | implicit_frame",
      "evidence_span": "short quoted fragment in original Hungarian",
      "confidence": "high | medium | low"
      // high = explicit, central, unambiguous. medium = clear but secondary or compressed. low = implied or structurally incomplete.
    }
  ]
}
```

# DECISION TABLE: narrative_function
| If the element... | → assign |
|---|---|
| Asserts something as fact or history | claim |
| Judges an actor, event, or state as good/bad/unfair | evaluation |
| Frames conditional or actual harm ("if X then catastrophe") | threat |
| Calls for resistance, action, opposition, or rally | mobilisation |
| Frames conditional or preventative danger ("beware of X") | warning |
| Commits to a future action, programme, or pledge | policy_promise |
| Is purely logistical (travel, scheduling) or background (context, history) with no narrative pressure | **DO NOT EXTRACT** |

# DECISION TABLE: confidence
| Condition | → assign |
|---|---|
| Explicit, unambiguous, central | high |
| Clear but secondary or compressed | medium |
| Implied, weak, or structurally incomplete | low |

# RULES (compact)
1. Extract only what is stated or linguistically signalled. No inferred intent, ideology, or hidden strategy.
2. One element = one actor + one claim/evaluation/threat/call. Do not merge unrelated claims.
3. Use exact surface forms for actors and targets. Do not normalise or translate names.
4. Do NOT extract background or logistics that carry no narrative pressure (historical recall, travel plans, procedural facts). If in doubt, omit.
5. Assign portrayed_role only where the text constructs it. If a speaker mobilises, defends, or protects → hero or hero_narrator for speaker_role. If weak or mixed → unclear.
6. Populate causal_claim only for explicit causation. Grammatical connectors (hogy, ami, amelyből) are NOT causal markers unless they introduce cause→effect logic. If causality is implied but weak, use causal_marker_surface = "implied" and confidence = "low".
7. Populate normative_direction only for explicit demands, prohibitions, obligations, or calls. "Therefore we must" is only valid if explicitly stated.
8. Do NOT infer hostility from criticism. Do NOT assign hero/villain to journalists. Do NOT invent policy goals.

# OUTPUT
Valid JSON only. Hungarian for text fields. English for labels. No commentary outside JSON.

Article:
{{article}}"""


def extract_from_article(
    article_text: str,
    llm_client: LLMClient,
    link: Optional[str] = None,
    date: Optional[str] = None,
    use_langfuse_prompt: bool = True,
    prompt_name: str = "narrative_extractor",
) -> Optional[dict]:
    """
    Extract narrative elements from a single article.
    
    Args:
        article_text: Article text
        llm_client: LLMClient instance
        link: Article URL (for metadata)
        date: Publication date (for metadata)
        use_langfuse_prompt: Whether to use Langfuse prompt template
        prompt_name: Name of Langfuse prompt to use
        
    Returns:
        Extracted narratives as dict, or None on failure
    """
    metadata = {
        "resource_link": link or "manual_input",
        "article_date": date or datetime.now().isoformat(),
        "project": "PoliticalNLP_2026"
    }
    
    try:
        if use_langfuse_prompt and llm_client.use_langfuse:
            # Use Langfuse prompt template
            result = llm_client.call_with_prompt_template(
                prompt_name=prompt_name,
                variables={"article": article_text},
                trace_name="narrative-extraction",
                metadata=metadata
            )
        else:
            # Use hardcoded prompts
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ANALYSIS_PROMPT.replace("{{article}}", article_text)}
            ]
            result = llm_client.call_openai(
                messages=messages,
                model=Config.NARRATIVE_MODEL,
                temperature=0.0,
                name="narrative-extraction",
                metadata=metadata
            )
        
        # Clean and parse JSON
        result = result.strip()
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        return json.loads(result)
    
    except Exception as e:
        print(f"Extraction failed for {link or 'article'}: {e}")
        return None


def extract_narratives(
    df: pd.DataFrame,
    output_column: str = "narratives",
    article_column: str = "article",
    link_column: str = "link",
    date_column: str = "publication_timestamp",
    use_langfuse: bool = None,
    prompt_name: str = "narrative_extractor",
    delay: float = None,
) -> pd.DataFrame:
    """
    Extract narrative elements from a DataFrame of articles.
    
    Args:
        df: Input DataFrame with articles
        output_column: Name for output column
        article_column: Name of column containing article text
        link_column: Name of column containing article URL
        date_column: Name of column containing publication date
        use_langfuse: Whether to use Langfuse tracking (autodects if None)
        prompt_name: Name of Langfuse prompt template
        delay: Seconds to wait between requests (uses Config.REQUEST_DELAY if None)
        
    Returns:
        DataFrame with additional column containing extracted narratives
    """
    delay = delay if delay is not None else Config.REQUEST_DELAY
    llm_client = LLMClient(use_langfuse=use_langfuse)
    
    results = []
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Extracting narratives"):
        article_text = row[article_column]
        link = row.get(link_column, "unknown")
        date = str(row.get(date_column, ""))
        
        narratives = extract_from_article(
            article_text=article_text,
            llm_client=llm_client,
            link=link,
            date=date,
            use_langfuse_prompt=llm_client.use_langfuse,
            prompt_name=prompt_name
        )
        
        results.append(narratives)
        time.sleep(delay)
    
    df[output_column] = results
    print(f"Extracted narratives for {len(df)} articles. Column: '{output_column}'")
    
    return df
