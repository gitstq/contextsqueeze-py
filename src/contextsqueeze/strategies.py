"""
Compression strategies for different content types.
"""

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CompressionResult:
    """Result of a compression operation."""

    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    strategy: str
    metadata: dict[str, Any]

    @property
    def savings_ratio(self) -> float:
        """Calculate token savings ratio."""
        if self.original_tokens == 0:
            return 0.0
        return (self.original_tokens - self.compressed_tokens) / self.original_tokens

    @property
    def savings_percent(self) -> float:
        """Calculate token savings percentage."""
        return self.savings_ratio * 100


class CompressionStrategy(ABC):
    """Base class for compression strategies."""

    name: str = "base"

    @abstractmethod
    def compress(self, text: str, target_ratio: float = 0.5) -> CompressionResult:
        """
        Compress the given text.

        Args:
            text: Input text to compress.
            target_ratio: Target compression ratio (0-1).

        Returns:
            CompressionResult with original and compressed text.
        """
        pass

    def _create_result(
        self,
        original: str,
        compressed: str,
        original_tokens: int,
        compressed_tokens: int,
        metadata: Optional[dict] = None,
    ) -> CompressionResult:
        """Helper to create a CompressionResult."""
        return CompressionResult(
            original_text=original,
            compressed_text=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            strategy=self.name,
            metadata=metadata or {},
        )


class SemanticCompression(CompressionStrategy):
    """
    Semantic compression using sentence importance scoring.
    Keeps key sentences and removes redundant/fluff content.
    """

    name = "semantic"

    # Keywords that indicate important sentences
    IMPORTANT_KEYWORDS = [
        "error", "exception", "failed", "success", "critical", "important",
        "warning", "deprecated", "note", "todo", "fixme", "bug",
        "must", "should", "required", "optional", "default",
    ]

    # Filler words/phrases to remove
    FILLER_PATTERNS = [
        r"\b(um|uh|like|you know|basically|literally|actually|honestly)\b",
        r"\b(in order to|due to the fact that|with regard to|in the event that)\b",
        r"\b(at this point in time|in the near future|for all intents and purposes)\b",
    ]

    def compress(self, text: str, target_ratio: float = 0.5) -> CompressionResult:
        """Compress text by removing filler and keeping important sentences."""
        from .tokenizer import TokenCounter

        counter = TokenCounter()
        original_tokens = counter.count(text)

        # Remove filler phrases
        compressed = text
        for pattern in self.FILLER_PATTERNS:
            compressed = re.sub(pattern, "", compressed, flags=re.IGNORECASE)

        # Split into sentences and score them
        sentences = self._split_sentences(compressed)
        if len(sentences) <= 3:
            # Too short to compress meaningfully
            return self._create_result(text, text, original_tokens, original_tokens, {"reason": "too_short"})

        scored = [(s, self._score_sentence(s)) for s in sentences]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Keep top sentences to meet target ratio
        target_sentences = max(1, int(len(sentences) * (1 - target_ratio)))
        kept = scored[:target_sentences]
        kept.sort(key=lambda x: sentences.index(x[0]))  # Restore original order

        compressed = " ".join(s for s, _ in kept)
        compressed_tokens = counter.count(compressed)

        return self._create_result(
            text,
            compressed,
            original_tokens,
            compressed_tokens,
            {"sentences_kept": target_sentences, "total_sentences": len(sentences)},
        )

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _score_sentence(self, sentence: str) -> int:
        """Score sentence importance."""
        score = 0
        lower = sentence.lower()

        # Length score (avoid very short sentences)
        words = len(sentence.split())
        if 5 <= words <= 30:
            score += 2
        elif words > 30:
            score += 1

        # Keyword score
        for keyword in self.IMPORTANT_KEYWORDS:
            if keyword in lower:
                score += 3

        # Code/content indicators
        if any(c in sentence for c in "`='{}"):
            score += 2
        if re.search(r'\d+', sentence):
            score += 1

        return score


class CodeCompression(CompressionStrategy):
    """
    Code-aware compression that preserves structure while removing comments and whitespace.
    """

    name = "code"

    def compress(self, text: str, target_ratio: float = 0.5) -> CompressionResult:
        """Compress code by removing comments and excess whitespace."""
        from .tokenizer import TokenCounter

        counter = TokenCounter()
        original_tokens = counter.count(text)

        compressed = text

        # Remove single-line comments (//, #)
        compressed = re.sub(r"\s*//.*$", "", compressed, flags=re.MULTILINE)
        compressed = re.sub(r"\s*#.*$", "", compressed, flags=re.MULTILINE)

        # Remove multi-line comments (/* */)
        compressed = re.sub(r"/\*.*?\*/", "", compressed, flags=re.DOTALL)

        # Remove docstrings (""" """ or ''' ''')
        compressed = re.sub(r'\s*""".*?"""', '"""..."""', compressed, flags=re.DOTALL)
        compressed = re.sub(r"\s*'''.*?'''", "'''...'''", compressed, flags=re.DOTALL)

        # Collapse multiple blank lines
        compressed = re.sub(r"\n{3,}", "\n\n", compressed)

        # Remove trailing whitespace
        compressed = re.sub(r"[ \t]+$", "", compressed, flags=re.MULTILINE)

        compressed_tokens = counter.count(compressed)

        return self._create_result(
            text,
            compressed,
            original_tokens,
            compressed_tokens,
            {"comments_removed": True, "whitespace_collapsed": True},
        )


class JSONCompression(CompressionStrategy):
    """
    JSON-specific compression that removes whitespace and optionally truncates arrays.
    """

    name = "json"

    def compress(self, text: str, target_ratio: float = 0.5) -> CompressionResult:
        """Compress JSON by minifying and optionally truncating large arrays."""
        from .tokenizer import TokenCounter

        counter = TokenCounter()
        original_tokens = counter.count(text)

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Not valid JSON, fall back to text compression
            return SemanticCompression().compress(text, target_ratio)

        # Minify JSON
        compressed = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

        # If still too large, truncate arrays
        if target_ratio > 0.3:
            data = self._truncate_arrays(data, max_items=10)
            compressed = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

        compressed_tokens = counter.count(compressed)

        return self._create_result(
            text,
            compressed,
            original_tokens,
            compressed_tokens,
            {"minified": True, "arrays_truncated": target_ratio > 0.3},
        )

    def _truncate_arrays(self, data: Any, max_items: int = 10) -> Any:
        """Recursively truncate arrays in JSON data."""
        if isinstance(data, list):
            if len(data) > max_items:
                truncated = data[:max_items]
                truncated.append(f"... ({len(data) - max_items} more items)")
                return truncated
            return [self._truncate_arrays(item, max_items) for item in data]
        elif isinstance(data, dict):
            return {k: self._truncate_arrays(v, max_items) for k, v in data.items()}
        return data


class TextSummarization(CompressionStrategy):
    """
    Extractive summarization for long text content.
    Uses paragraph-based extraction with key phrase scoring.
    """

    name = "text"

    def compress(self, text: str, target_ratio: float = 0.5) -> CompressionResult:
        """Compress text using extractive summarization."""
        from .tokenizer import TokenCounter

        counter = TokenCounter()
        original_tokens = counter.count(text)

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) <= 2:
            return SemanticCompression().compress(text, target_ratio)

        # Score paragraphs
        scored = [(p, self._score_paragraph(p)) for p in paragraphs]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Keep top paragraphs
        keep_count = max(1, int(len(paragraphs) * (1 - target_ratio)))
        kept = scored[:keep_count]
        kept.sort(key=lambda x: paragraphs.index(x[0]))

        compressed = "\n\n".join(p for p, _ in kept)
        compressed_tokens = counter.count(compressed)

        return self._create_result(
            text,
            compressed,
            original_tokens,
            compressed_tokens,
            {"paragraphs_kept": keep_count, "total_paragraphs": len(paragraphs)},
        )

    def _score_paragraph(self, paragraph: str) -> int:
        """Score paragraph importance."""
        score = 0
        lower = paragraph.lower()

        # Length preference
        words = len(paragraph.split())
        if 20 <= words <= 200:
            score += 3
        elif words > 10:
            score += 1

        # Content indicators
        if any(c in paragraph for c in "`='{}"):
            score += 2
        if re.search(r'\d+', paragraph):
            score += 1
        if re.search(r'(error|exception|warning|important|note)', lower):
            score += 3

        return score
