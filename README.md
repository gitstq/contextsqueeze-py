<p align="center">
  <img src="https://img.shields.io/badge/ContextSqueeze-LLM%20Compression-blue?style=for-the-badge" alt="ContextSqueeze">
</p>

<h1 align="center">ContextSqueeze</h1>

<p align="center">
  <b>Lightweight LLM Context Compression & Intelligent Routing Toolkit</b><br>
  Reduce token usage by 50-80% while preserving semantic meaning
</p>

<p align="center">
  <a href="https://github.com/gitstq/contextsqueeze-py/releases"><img src="https://img.shields.io/github/v/release/gitstq/contextsqueeze-py?style=flat-square" alt="Release"></a>
  <a href="https://github.com/gitstq/contextsqueeze-py/blob/main/LICENSE"><img src="https://img.shields.io/github/license/gitstq/contextsqueeze-py?style=flat-square" alt="License"></a>
  <a href="https://github.com/gitstq/contextsqueeze-py/actions"><img src="https://img.shields.io/github/actions/workflow/status/gitstq/contextsqueeze-py/ci.yml?style=flat-square" alt="CI"></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square" alt="Python">
</p>

---

## 🎉 Project Introduction

ContextSqueeze is a high-performance, lightweight toolkit designed to intelligently compress LLM prompts and context windows. It automatically detects content types, routes them to optimal compression strategies, and significantly reduces token usage without losing semantic meaning.

**Why ContextSqueeze?**
- 💰 **Save Money**: Reduce API costs by 50-80%
- ⚡ **Faster Responses**: Shorter prompts = faster inference
- 🧠 **Smarter Routing**: Auto-detects content type and applies best strategy
- 🔒 **Local-First**: All processing happens locally, no data leaves your machine
- 🛠️ **Developer-Friendly**: Simple CLI and Python API

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| **Auto Content Detection** | Automatically identifies code, JSON, logs, markdown, and plain text |
| **4 Compression Strategies** | Semantic, Code, JSON, and Text summarization |
| **Token Counting** | Accurate token counting for GPT-4, Claude, and other models |
| **Cost Estimation** | Real-time API cost calculation before and after compression |
| **Batch Processing** | Process JSONL files with multiple messages at once |
| **Rich CLI Output** | Beautiful terminal output with tables and progress indicators |
| **Message Compression** | Compress entire chat message histories |

## 🚀 Quick Start

### Installation

```bash
pip install contextsqueeze
```

### CLI Usage

```bash
# Compress a file
ctxsq compress -f large_prompt.txt --ratio 0.5

# Detect content type
ctxsq detect myfile.py

# List strategies
ctxsq strategies

# Batch process
ctxsq batch messages.jsonl -o compressed.jsonl

# Pipe from stdin
cat log.txt | ctxsq compress --ratio 0.6
```

### Python API

```python
from contextsqueeze import ContextCompressor

# Initialize compressor
compressor = ContextCompressor(model="gpt-4")

# Compress text (auto-detects content type)
result = compressor.compress(
    text=long_text,
    target_ratio=0.5
)

print(f"Saved {result.savings_percent}% tokens")
print(f"Compressed: {result.compressed_text}")

# Get detailed stats
stats = compressor.get_stats(result)
print(f"Cost saved: ${stats['cost_saved_usd']}")

# Compress chat messages
messages = [
    {"role": "user", "content": long_user_message},
    {"role": "assistant", "content": long_assistant_response},
]
compressed = compressor.compress_messages(messages, target_ratio=0.5)
```

## 📖 Detailed Usage Guide

### Compression Strategies

| Strategy | Best For | How It Works |
|----------|----------|--------------|
| **semantic** | General text, articles | Sentence importance scoring + filler removal |
| **code** | Source code files | Comment removal + whitespace collapse |
| **json** | JSON data, API responses | Minification + array truncation |
| **text** | Long documents, logs | Paragraph-based extractive summarization |

### Content Type Detection

ContextSqueeze automatically detects these content types:

- **Code**: Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, and more
- **JSON**: API responses, configuration files
- **Markdown**: Documentation, README files
- **Logs**: Application logs with timestamps
- **HTML/XML**: Web content
- **Stack Traces**: Error traces and exceptions

### Advanced Options

```bash
# Specify strategy manually
ctxsq compress -f data.json --strategy json --ratio 0.7

# Use specific model for token counting
ctxsq --model gpt-4o compress -f prompt.txt

# Higher compression ratio
ctxsq compress -f article.md --ratio 0.8
```

## 💡 Design Philosophy

ContextSqueeze was designed with three principles:

1. **Intelligence over Brute Force**: Instead of blindly truncating, we analyze content structure and preserve meaning
2. **Zero Dependencies for Core**: The core library has minimal dependencies for easy integration
3. **Developer Experience First**: Beautiful CLI, clear API, comprehensive tests

### Architecture

```
Input Text
    |
    v
[ContentRouter] --> Detects ContentType
    |
    v
[Strategy Selector] --> Picks optimal strategy
    |
    v
[Compressor] --> Applies compression
    |
    v
[TokenCounter] --> Calculates savings
    |
    v
CompressionResult
```

## 📦 Packaging & Deployment

### Build from Source

```bash
git clone https://github.com/gitstq/contextsqueeze-py.git
cd contextsqueeze-py
pip install -e ".[dev]"
pytest
```

### Run Tests

```bash
pytest tests/ -v --cov=contextsqueeze
```

### Code Quality

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ for the AI developer community
</p>
