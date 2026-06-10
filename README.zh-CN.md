<p align="center">
  <img src="https://img.shields.io/badge/ContextSqueeze-LLM%20压缩工具-blue?style=for-the-badge" alt="ContextSqueeze">
</p>

<h1 align="center">ContextSqueeze</h1>

<p align="center">
  <b>轻量级 LLM 上下文压缩与智能路由工具包</b><br>
  在保留语义的同时减少 50-80% 的 Token 使用量
</p>

<p align="center">
  <a href="https://github.com/gitstq/contextsqueeze-py/releases"><img src="https://img.shields.io/github/v/release/gitstq/contextsqueeze-py?style=flat-square" alt="Release"></a>
  <a href="https://github.com/gitstq/contextsqueeze-py/blob/main/LICENSE"><img src="https://img.shields.io/github/license/gitstq/contextsqueeze-py?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square" alt="Python">
</p>

---

## 🎉 项目介绍

ContextSqueeze 是一个高性能、轻量级的工具包，用于智能压缩 LLM 提示词和上下文窗口。它能自动检测内容类型，将其路由到最优压缩策略，并在不丢失语义的情况下显著减少 Token 使用量。

**为什么选择 ContextSqueeze？**
- 💰 **省钱**: 减少 50-80% 的 API 调用成本
- ⚡ **响应更快**: 更短的提示词 = 更快的推理速度
- 🧠 **智能路由**: 自动检测内容类型并应用最佳策略
- 🔒 **本地优先**: 所有处理都在本地完成，数据不会离开你的机器
- 🛠️ **开发者友好**: 简洁的 CLI 和 Python API

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| **自动内容检测** | 自动识别代码、JSON、日志、Markdown 和普通文本 |
| **4 种压缩策略** | 语义压缩、代码压缩、JSON 压缩、文本摘要 |
| **Token 计数** | 支持 GPT-4、Claude 等模型的精确 Token 计数 |
| **成本估算** | 实时计算压缩前后的 API 成本 |
| **批量处理** | 一次性处理包含多条消息的 JSONL 文件 |
| **精美 CLI 输出** | 带有表格和进度指示器的优雅终端输出 |
| **消息压缩** | 压缩整个聊天消息历史 |

## 🚀 快速开始

### 安装

```bash
pip install contextsqueeze
```

### CLI 使用

```bash
# 压缩文件
ctxsq compress -f large_prompt.txt --ratio 0.5

# 检测内容类型
ctxsq detect myfile.py

# 列出策略
ctxsq strategies

# 批量处理
ctxsq batch messages.jsonl -o compressed.jsonl

# 从标准输入管道
 cat log.txt | ctxsq compress --ratio 0.6
```

### Python API

```python
from contextsqueeze import ContextCompressor

# 初始化压缩器
compressor = ContextCompressor(model="gpt-4")

# 压缩文本（自动检测内容类型）
result = compressor.compress(
    text=long_text,
    target_ratio=0.5
)

print(f"节省了 {result.savings_percent}% 的 Token")
print(f"压缩后: {result.compressed_text}")

# 获取详细统计
stats = compressor.get_stats(result)
print(f"节省成本: ${stats['cost_saved_usd']}")

# 压缩聊天消息
messages = [
    {"role": "user", "content": long_user_message},
    {"role": "assistant", "content": long_assistant_response},
]
compressed = compressor.compress_messages(messages, target_ratio=0.5)
```

## 📖 详细使用指南

### 压缩策略

| 策略 | 适用场景 | 工作原理 |
|------|----------|----------|
| **semantic** | 普通文本、文章 | 句子重要性评分 + 去除冗余 |
| **code** | 源代码文件 | 删除注释 + 折叠空白 |
| **json** | JSON 数据、API 响应 | 最小化 + 数组截断 |
| **text** | 长文档、日志 | 基于段落的提取式摘要 |

### 内容类型检测

ContextSqueeze 自动检测以下内容类型：

- **代码**: Python、JavaScript、TypeScript、Go、Rust、Java、C/C++ 等
- **JSON**: API 响应、配置文件
- **Markdown**: 文档、README 文件
- **日志**: 带时间戳的应用日志
- **HTML/XML**: Web 内容
- **堆栈跟踪**: 错误跟踪和异常

## 📄 开源协议

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  用 ❤️ 为 AI 开发者社区打造
</p>
