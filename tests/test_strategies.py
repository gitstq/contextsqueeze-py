"""
Tests for compression strategies.
"""

import pytest

from contextsqueeze.strategies import (
    CodeCompression,
    JSONCompression,
    SemanticCompression,
    TextSummarization,
)


class TestSemanticCompression:
    def test_compress_text(self):
        strategy = SemanticCompression()
        text = "This is a test sentence. It contains important error information. " * 20
        result = strategy.compress(text, target_ratio=0.5)
        assert result.strategy == "semantic"
        assert result.savings_percent >= 0

    def test_short_text_unchanged(self):
        strategy = SemanticCompression()
        text = "Short text."
        result = strategy.compress(text, target_ratio=0.5)
        assert result.savings_percent == 0 or "too_short" in result.metadata.get("reason", "")


class TestCodeCompression:
    def test_remove_comments(self):
        strategy = CodeCompression()
        code = '''
def hello():
    # This is a comment
    return "world"
'''
        result = strategy.compress(code, target_ratio=0.3)
        assert "# This is a comment" not in result.compressed_text
        assert 'def hello():' in result.compressed_text

    def test_collapse_whitespace(self):
        strategy = CodeCompression()
        code = "def a():\n\n\n\n    pass\n"
        result = strategy.compress(code)
        assert "\n\n\n\n" not in result.compressed_text


class TestJSONCompression:
    def test_minify_json(self):
        strategy = JSONCompression()
        data = '{\n  "key": "value",\n  "num": 123\n}'
        result = strategy.compress(data)
        assert result.compressed_text == '{"key":"value","num":123}'

    def test_truncate_arrays(self):
        strategy = JSONCompression()
        data = '{"items": [' + ','.join([str(i) for i in range(20)]) + ']}'
        result = strategy.compress(data, target_ratio=0.5)
        assert "more items" in result.compressed_text


class TestTextSummarization:
    def test_summarize_long_text(self):
        strategy = TextSummarization()
        paragraphs = [f"Paragraph {i} with some important content about errors and bugs." for i in range(10)]
        text = "\n\n".join(paragraphs)
        result = strategy.compress(text, target_ratio=0.5)
        assert result.strategy == "text"
        assert result.savings_percent >= 0
