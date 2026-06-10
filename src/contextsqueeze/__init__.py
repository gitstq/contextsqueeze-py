"""
ContextSqueeze - Lightweight LLM Context Compression & Intelligent Routing

A high-performance toolkit for compressing LLM prompts, routing content intelligently,
and reducing token usage by 50-80% while preserving semantic meaning.
"""

__version__ = "0.1.0"
__author__ = "ContextSqueeze Team"

from .compressor import ContextCompressor
from .router import ContentRouter, ContentType
from .tokenizer import TokenCounter
from .strategies import (
    CompressionStrategy,
    SemanticCompression,
    CodeCompression,
    JSONCompression,
    TextSummarization,
    CompressionResult,
)

__all__ = [
    "ContextCompressor",
    "ContentRouter",
    "ContentType",
    "TokenCounter",
    "CompressionStrategy",
    "SemanticCompression",
    "CodeCompression",
    "JSONCompression",
    "TextSummarization",
    "CompressionResult",
]
