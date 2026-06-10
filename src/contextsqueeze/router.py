"""
Content type detection and intelligent routing.
"""

import json
import re
from enum import Enum, auto
from typing import Optional


class ContentType(Enum):
    """Supported content types for compression."""

    TEXT = auto()
    CODE = auto()
    JSON = auto()
    MARKDOWN = auto()
    LOG = auto()
    STACK_TRACE = auto()
    HTML = auto()
    YAML = auto()
    CSV = auto()
    XML = auto()


class ContentRouter:
    """Intelligent content router that detects content type and routes to appropriate compressor."""

    # File extension to content type mapping
    EXTENSION_MAP = {
        ".py": ContentType.CODE,
        ".js": ContentType.CODE,
        ".ts": ContentType.CODE,
        ".java": ContentType.CODE,
        ".go": ContentType.CODE,
        ".rs": ContentType.CODE,
        ".cpp": ContentType.CODE,
        ".c": ContentType.CODE,
        ".h": ContentType.CODE,
        ".rb": ContentType.CODE,
        ".php": ContentType.CODE,
        ".swift": ContentType.CODE,
        ".kt": ContentType.CODE,
        ".json": ContentType.JSON,
        ".md": ContentType.MARKDOWN,
        ".markdown": ContentType.MARKDOWN,
        ".log": ContentType.LOG,
        ".html": ContentType.HTML,
        ".htm": ContentType.HTML,
        ".yaml": ContentType.YAML,
        ".yml": ContentType.YAML,
        ".csv": ContentType.CSV,
        ".xml": ContentType.XML,
    }

    # Content patterns for detection
    PATTERNS = {
        ContentType.JSON: re.compile(r"^\s*[\{\[]"),
        ContentType.HTML: re.compile(r"<(!DOCTYPE|html|body|div|span)[\s>]"),
        ContentType.XML: re.compile(r"<\?xml\s+version="),
        ContentType.STACK_TRACE: re.compile(
            r"(Traceback|Exception|Error)\s*\(|at\s+\w+\.\w+\(|Caused by:"
        ),
        ContentType.LOG: re.compile(
            r"^\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}|\[\w+\]\s+\w+:|\w+:\d+:\s+(INFO|WARN|ERROR|DEBUG)"
        ),
        ContentType.CODE: re.compile(
            r"^(def\s+|class\s+|function\s+|const\s+|let\s+|var\s+|import\s+|from\s+|#include|package\s+|public\s+class)"
        ),
        ContentType.MARKDOWN: re.compile(r"^(#{1,6}\s|```|\[.*?\]\(.*?\)|\*\*|__|\|.*\|)"),
        ContentType.YAML: re.compile(r"^(\w+:\s|---\s*$)"),
        ContentType.CSV: re.compile(r"^[^,]+,[^,]+,[^,]+"),
    }

    @classmethod
    def detect(cls, content: str, filename: Optional[str] = None) -> ContentType:
        """
        Detect content type from content string and optional filename.

        Args:
            content: The content to analyze.
            filename: Optional filename for extension-based detection.

        Returns:
            Detected ContentType.
        """
        # Check filename extension first
        if filename:
            ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
            if ext in cls.EXTENSION_MAP:
                return cls.EXTENSION_MAP[ext]

        # Check content patterns
        first_lines = "\n".join(content.split("\n")[:10])
        for content_type, pattern in cls.PATTERNS.items():
            if pattern.search(first_lines):
                return content_type

        # Try JSON parsing as fallback
        try:
            json.loads(content)
            return ContentType.JSON
        except (json.JSONDecodeError, ValueError):
            pass

        return ContentType.TEXT

    @classmethod
    def get_strategy_name(cls, content_type: ContentType) -> str:
        """
        Get recommended compression strategy name for content type.

        Args:
            content_type: Detected content type.

        Returns:
            Strategy name string.
        """
        strategy_map = {
            ContentType.CODE: "code",
            ContentType.JSON: "json",
            ContentType.LOG: "text",
            ContentType.STACK_TRACE: "text",
            ContentType.MARKDOWN: "text",
            ContentType.HTML: "text",
            ContentType.YAML: "json",
            ContentType.CSV: "text",
            ContentType.XML: "text",
            ContentType.TEXT: "semantic",
        }
        return strategy_map.get(content_type, "semantic")
