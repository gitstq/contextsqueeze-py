"""
Main compressor orchestrator that routes content to appropriate strategies.
"""

from typing import Optional

from .router import ContentRouter, ContentType
from .strategies import (
    CodeCompression,
    CompressionResult,
    CompressionStrategy,
    JSONCompression,
    SemanticCompression,
    TextSummarization,
)
from .tokenizer import TokenCounter


class ContextCompressor:
    """
    Main entry point for context compression.
    Automatically detects content type and applies optimal compression strategy.
    """

    STRATEGIES: dict[str, CompressionStrategy] = {
        "semantic": SemanticCompression(),
        "code": CodeCompression(),
        "json": JSONCompression(),
        "text": TextSummarization(),
    }

    def __init__(self, model: str = "gpt-4", default_strategy: str = "semantic"):
        """
        Initialize compressor.

        Args:
            model: LLM model name for token counting.
            default_strategy: Default compression strategy name.
        """
        self.token_counter = TokenCounter(model)
        self.default_strategy = default_strategy

    def compress(
        self,
        text: str,
        strategy: Optional[str] = None,
        target_ratio: float = 0.5,
        filename: Optional[str] = None,
    ) -> CompressionResult:
        """
        Compress text using specified or auto-detected strategy.

        Args:
            text: Input text to compress.
            strategy: Compression strategy name (auto-detected if None).
            target_ratio: Target compression ratio (0-1).
            filename: Optional filename for content type detection.

        Returns:
            CompressionResult with compression metrics.
        """
        if not text or not text.strip():
            return CompressionResult(
                original_text=text,
                compressed_text=text,
                original_tokens=0,
                compressed_tokens=0,
                strategy="none",
                metadata={"reason": "empty_input"},
            )

        # Auto-detect strategy if not specified
        if strategy is None:
            content_type = ContentRouter.detect(text, filename)
            strategy = ContentRouter.get_strategy_name(content_type)

        # Get strategy instance
        compressor = self.STRATEGIES.get(strategy, self.STRATEGIES[self.default_strategy])

        # Perform compression
        result = compressor.compress(text, target_ratio)

        return result

    def compress_messages(
        self,
        messages: list[dict],
        target_ratio: float = 0.5,
        compress_content: bool = True,
    ) -> list[dict]:
        """
        Compress a list of chat messages.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            target_ratio: Target compression ratio.
            compress_content: Whether to compress message content.

        Returns:
            Compressed messages list.
        """
        if not compress_content:
            return messages

        compressed = []
        for msg in messages:
            new_msg = dict(msg)
            content = msg.get("content", "")
            if isinstance(content, str) and content:
                result = self.compress(content, target_ratio=target_ratio)
                new_msg["content"] = result.compressed_text
                new_msg["_compression_meta"] = {
                    "strategy": result.strategy,
                    "savings": result.savings_percent,
                }
            compressed.append(new_msg)

        return compressed

    def get_stats(self, result: CompressionResult) -> dict:
        """
        Get human-readable compression statistics.

        Args:
            result: CompressionResult to analyze.

        Returns:
            Dictionary with compression statistics.
        """
        original_cost = self.token_counter.estimate_cost(result.original_tokens)
        compressed_cost = self.token_counter.estimate_cost(result.compressed_tokens)

        return {
            "strategy": result.strategy,
            "original_tokens": result.original_tokens,
            "compressed_tokens": result.compressed_tokens,
            "tokens_saved": result.original_tokens - result.compressed_tokens,
            "savings_percent": round(result.savings_percent, 2),
            "original_cost_usd": round(original_cost, 6),
            "compressed_cost_usd": round(compressed_cost, 6),
            "cost_saved_usd": round(original_cost - compressed_cost, 6),
            "metadata": result.metadata,
        }
