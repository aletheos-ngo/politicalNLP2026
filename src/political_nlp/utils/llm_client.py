"""
Unified LLM client for OpenAI/Anthropic API calls with Langfuse tracking.
Centralizes all LLM interactions to avoid code duplication.
"""

import json
import time
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

import litellm
from langfuse import Langfuse
from langfuse.openai import openai

from ..config import Config


class LLMClient:
    """
    Unified client for LLM API calls with standardized error handling,
    retry logic, and optional Langfuse tracking.
    """
    
    def __init__(self, use_langfuse: bool = None):
        """
        Initialize LLM client.
        
        Args:
            use_langfuse: Whether to use Langfuse tracking. If None, autodetetect from config.
        """
        self.use_langfuse = use_langfuse if use_langfuse is not None else Config.use_langfuse()
        
        if self.use_langfuse:
            self.langfuse = Langfuse(
                public_key=Config.LANGFUSE_PUBLIC_KEY,
                secret_key=Config.LANGFUSE_SECRET_KEY,
                host=Config.LANGFUSE_HOST
            )
        else:
            self.langfuse = None
    
    def call_openai(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.0,
        response_format=None,
        name: str = None,
        metadata: Optional[Dict] = None,
        langfuse_prompt=None,
        trace_id: str = None,
        max_retries: int = 3,
    ) -> Any:
        """
        Call OpenAI API with standardized error handling.
        
        Args:
            messages: Chat messages
            model: Model name (defaults to Config.NARRATIVE_MODEL)
            temperature: Sampling temperature
            response_format: Pydantic model for structured output
            name: Name for Langfuse tracking
            metadata: Metadata for Langfuse
            langfuse_prompt: Langfuse prompt template
            trace_id: Langfuse trace ID
            max_retries: Maximum retry attempts
            
        Returns:
            Response content (str or Pydantic model instance)
        """
        model = model or Config.NARRATIVE_MODEL
        
        for attempt in range(max_retries):
            try:
                if self.use_langfuse:
                    # Use Langfuse-wrapped OpenAI client
                    response = openai.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        response_format=response_format,
                        name=name,
                        metadata=metadata or {},
                        langfuse_prompt=langfuse_prompt,
                        trace_id=trace_id,
                    )
                else:
                    # Use litellm for standard OpenAI calls
                    response = litellm.completion(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        response_format=response_format,
                    )
                
                content = response.choices[0].message.content
                
                # If response_format is a Pydantic model, parse the JSON
                if response_format and isinstance(response_format, type) and issubclass(response_format, BaseModel):
                    return response_format.model_validate_json(content)
                
                return content
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def call_with_prompt_template(
        self,
        prompt_name: str,
        variables: Dict[str, str],
        model: str = None,
        trace_name: str = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Call LLM using a Langfuse prompt template.
        
        Args:
            prompt_name: Name of the Langfuse prompt
            variables: Template variables (e.g., {"article": "text..."})
            model: Model override
            trace_name: Trace name for Langfuse
            metadata: Additional metadata
            
        Returns:
            Response content as string
        """
        if not self.use_langfuse:
            raise ValueError("Langfuse tracking must be enabled to use prompt templates")
        
        # Fetch prompt template
        prompt_template = self.langfuse.get_prompt(prompt_name)
        messages = prompt_template.compile(**variables)
        
        # Start trace if requested
        trace = None
        if trace_name:
            trace = self.langfuse.trace(
                name=trace_name,
                input={"prompt": prompt_name, **variables},
                metadata=metadata or {}
            )
        
        # Call with template
        response = self.call_openai(
            messages=messages,
            model=model or prompt_template.config.get("model"),
            temperature=prompt_template.config.get("temperature", 0.0),
            langfuse_prompt=prompt_template,
            trace_id=trace.id if trace else None,
        )
        
        if trace:
            trace.update(output=response)
        
        return response
    
    def call_anthropic(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        system_prompt: str = None,
    ) -> str:
        """
        Call Anthropic Claude API.
        
        Args:
            messages: Chat messages
            model: Model name (defaults to Config.BRIEF_MODEL)
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            system_prompt: System prompt
            
        Returns:
            Response content as string
        """
        from anthropic import Anthropic
        
        model = model or Config.BRIEF_MODEL
        client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        
        # Anthropic uses separate system parameter
        user_messages = [m for m in messages if m["role"] != "system"]
        if not system_prompt and any(m["role"] == "system" for m in messages):
            system_prompt = next(m["content"] for m in messages if m["role"] == "system")
        
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=user_messages,
        )
        
        return response.content[0].text
