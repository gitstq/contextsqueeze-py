"""
Token counting utilities for various LLM providers.
"""

import re
from typing import Optional

import tiktoken


class TokenCounter:
    """Unified token counter supporting multiple LLM providers."""

    # Approximate tokens per character for fallback estimation
    CHARS_PER_TOKEN = 4.0

    def __init__(self, model: str = "gpt-4"):
        """
        Initialize token counter.

        Args:
            model: Model name for encoding selection.
        """
        self.model = model
        self._encoder: Optional[tiktoken.Encoding] = None
        self._init_encoder()

    def _init_encoder(self) -> None:
        """Initialize tiktoken encoder based on model name."""
        try:
            if "gpt-4" in self.model or "gpt-3.5" in self.model:
                self._encoder = tiktoken.encoding_for_model(self.model)
            elif "claude" in self.model.lower():
                # Claude uses roughly similar tokenization to GPT-4
                self._encoder = tiktoken.get_encoding("cl100k_base")
            else:
                self._encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self._encoder = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Input text.

        Returns:
            Token count.
        """
        if not text:
            return 0
        if self._encoder:
            return len(self._encoder.encode(text))
        return int(len(text) / self.CHARS_PER_TOKEN)

    def count_messages(self, messages: list[dict]) -> int:
        """
        Count tokens in a list of chat messages.

        Args:
            messages: List of message dicts with 'role' and 'content'.

        Returns:
            Total token count.
        """
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total += self.count(content)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        total += self.count(part["text"])
            # Add overhead for role tokens
            total += 4
        return total

    def estimate_cost(self, tokens: int, model: Optional[str] = None) -> float:
        """
        Estimate API cost based on token count.

        Args:
            tokens: Number of tokens.
            model: Model name (uses instance default if not provided).

        Returns:
            Estimated cost in USD.
        """
        model = model or self.model
        # Per 1K tokens pricing (approximate)
        pricing = {
            "gpt-4": 0.03,
            "gpt-4o": 0.005,
            "gpt-3.5-turbo": 0.0005,
            "claude-3-opus": 0.015,
            "claude-3-sonnet": 0.003,
        }
        rate = pricing.get(model, 0.01)
        return (tokens / 1000) * rate
