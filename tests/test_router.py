"""
Tests for content router.
"""

from contextsqueeze.router import ContentRouter, ContentType


class TestContentRouter:
    def test_detect_python_code(self):
        code = "def hello():\n    return 'world'"
        result = ContentRouter.detect(code, "test.py")
        assert result == ContentType.CODE

    def test_detect_json(self):
        data = '{"key": "value"}'
        result = ContentRouter.detect(data, "data.json")
        assert result == ContentType.JSON

    def test_detect_markdown(self):
        md = "# Heading\n\nSome text"
        result = ContentRouter.detect(md, "readme.md")
        assert result == ContentType.MARKDOWN

    def test_detect_html(self):
        html = "<html><body>Hello</body></html>"
        result = ContentRouter.detect(html)
        assert result == ContentType.HTML

    def test_detect_log(self):
        log = "2024-01-01 10:00:00 INFO Starting application"
        result = ContentRouter.detect(log)
        assert result == ContentType.LOG

    def test_detect_stack_trace(self):
        trace = "Traceback (most recent call last):\n  File \"test.py\""
        result = ContentRouter.detect(trace)
        assert result == ContentType.STACK_TRACE

    def test_detect_text_fallback(self):
        text = "Just some plain text without any special markers."
        result = ContentRouter.detect(text)
        assert result == ContentType.TEXT

    def test_get_strategy_name(self):
        assert ContentRouter.get_strategy_name(ContentType.CODE) == "code"
        assert ContentRouter.get_strategy_name(ContentType.JSON) == "json"
        assert ContentRouter.get_strategy_name(ContentType.TEXT) == "semantic"
