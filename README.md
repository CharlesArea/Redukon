# 🔥 Redukon

### Reduce Your Tokens. Keep Your Intent.

<p align="center">
  <a href="https://pypi.org/project/redukon/">
    <img src="https://img.shields.io/pypi/v/redukon.svg?color=%23ff6b6b" alt="PyPI">
  </a>
  <a href="https://pypi.org/project/redukon/">
    <img src="https://img.shields.io/pypi/pyversions/redukon.svg?color=%23ff6b6b" alt="Python">
  </a>
  <a href="https://github.com/CharlesArea/Redukon/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/CharlesArea/Redukon?color=%23ff6b6b" alt="License">
  </a>
  <a href="https://github.com/CharlesArea/Redukon/stargazers">
    <img src="https://img.shields.io/github/stars/CharlesArea/Redukon?style=social" alt="Stars">
  </a>
</p>

---

## 📋 Table of Contents

- [✨ What is Redukon?](#-what-is-redukon)
- [🚀 Quick Start](#-quick-start)
- [📖 CLI Usage](#-cli-usage)
  - [redukon onboard](#redukon-onboard)
  - [redukon rewrite](#redukon-rewrite)
  - [redukon serve](#redukon-serve)
- [🌐 API Usage](#-api-usage)
  - [Non-Streaming Example](#non-streaming-example)
  - [Streaming Example](#streaming-example)
  - [API Parameters](#api-parameters)
- [🐳 Docker](#-docker)
- [📦 Batch Mode](#-batch-mode)
- [⚡ Example](#-example)
- [🔧 Options](#-options)
- [🛠️ Requirements](#️-requirements)
- [📝 License](#-license)

---

## ✨ What is Redukon?

Redukon is a **token-saving prompt rewriter** that uses local small AI models to optimize your prompts — reducing token count while keeping the core intent intact.

**No API keys needed.** Runs entirely offline with [Ollama](https://ollama.com).

💡 **Perfect for:**
- Saving money on API calls
- Fitting more context into LLM windows
- Making prompts more efficient
- Building into your own apps via API

---

## 🚀 Quick Start

```bash
# Install from PyPI
pip install redukon

# Or install latest from GitHub
pip install -e https://github.com/CharlesArea/Redukon.git

# One-time setup (installs Ollama + picks a model)
redukon onboard
```

---

## 📖 CLI Usage

### `redukon onboard`
Interactive setup wizard:
1. Checks if Ollama is installed
2. Installs Ollama if needed
3. Choose your model:
   | Model | Size | Best For |
   |-------|------|----------|
   | `qwen2.5:0.5b` | 397MB | Speed & minimal resources |
   | `llama3.2:1b` | 1.9GB | Balanced |
   | `phi3:3.8b` | 2.3GB | Better quality |

### `redukon rewrite`
Rewrite your prompts from command line:

```bash
# Basic
redukon rewrite -i "Please write a comprehensive Python function..."

# From file
redukon rewrite -i @long-prompt.txt -o optimized.txt

# Custom temperature (lower = more focused)
redukon rewrite -i "prompt" --temp 0.3
```

### `redukon serve`
Start the API server:

```bash
# Default port 8000
redukon serve

# Custom port
redukon serve --port 9000
redukon serve --host 127.0.0.1 --port 8080
```

---

## 🌐 API Usage

### Start Server
```bash
redukon serve
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rewrite` | POST | Rewrite a prompt (non-streaming) |
| `/rewrite/stream` | POST | Rewrite a prompt (streaming) |
| `/health` | GET | Health check |

### Non-Streaming Example

```bash
curl -X POST http://localhost:8000/rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Please write a comprehensive Python function that takes a list of integers...",
    "model": "qwen2.5:0.5b",
    "temperature": 0.3
  }'
```

### Streaming Example

```bash
curl -X POST http://localhost:8000/rewrite/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your prompt here"}'
```

**Response (SSE format):**
```
data: {"chunk": "Write a "}
data: {"chunk": "Python function..."}
data: {"done": true, "original_tokens": 87, "optimized_tokens": 42, "saved_tokens": 45, "saved_percent": 52}
```

### Example Response

```json
{
  "optimized_prompt": "Write a Python function that filters even numbers from a list...",
  "original_tokens": 87,
  "optimized_tokens": 42,
  "saved_tokens": 45,
  "saved_percent": 52
}
```

### API Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | The prompt to optimize |
| `model` | string | No | Model name (default: from config) |
| `temperature` | float | No | Temperature 0.0-1.0 (default: 0.3) |

---

## 📝 Logging

API requests are logged to `log/api-YYYY-MM-DD.log`:

```
[2026-03-10 12:00:00] [REQUEST] input_length=250, model=qwen2.5:0.5b
[2026-03-10 12:00:05] [RESPONSE] output_length=120, original_tokens=62, optimized_tokens=30, saved_tokens=32, saved_percent=51%
[2026-03-10 12:00:05] [ERROR] Generation failed: Ollama not running
```

---

## 🐳 Docker

### Option 1: API Server Only (connects to Ollama on host)

```bash
# Build image
docker build -t redukon .

# Run (ensure Ollama is running on host)
docker run -d -p 8000:8000 --network host redukon
```

### Option 2: Full Stack with docker-compose

```bash
# Start both Redukon API and Ollama
docker-compose up -d

# Stop
docker-compose down
```

---

## 📦 Batch Mode

Process multiple prompts at once!

### CLI

```bash
# From file with multiple prompts (one per line)
redukon batch -i prompts.txt

# Multiple files
redukon batch -i @file1.txt @file2.txt

# With output
redukon batch -i prompts.txt -o results/
redukon batch -i prompts.txt -o results.json
```

### API

```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "First prompt to optimize",
      "Second prompt to optimize",
      "Third prompt to optimize"
    ],
    "model": "qwen2.5:0.5b",
    "temperature": 0.3
  }'
```

**Response:**
```json
{
  "results": [
    {"index": 0, "original": "...", "optimized_prompt": "...", "saved_tokens": 10, "saved_percent": 25},
    {"index": 1, "original": "...", "optimized_prompt": "...", "saved_tokens": 15, "saved_percent": 30}
  ],
  "summary": {
    "total": 2,
    "processed": 2,
    "total_original_tokens": 100,
    "total_saved_tokens": 25,
    "overall_saved_percent": 25
  }
}
```

---

## ⚡ Example

| Before (87 tokens) | After (42 tokens) |
|--------------------|-------------------|
| "Please write a comprehensive Python function that takes a list of integers as input and returns a new list containing only the even numbers from the original list. The function should handle edge cases like empty lists, lists with no even numbers, and lists with negative numbers. Please include proper type hints, docstrings, and error handling." | "Write a Python function that filters even numbers from a list. Include type hints, error handling, and docstrings." |

📉 **Savings: ~52%** 

---

## 🔧 Options

| Flag | Description | Default |
|------|-------------|---------|
| `-i, --input` | Prompt or `@file.txt` | Required |
| `-o, --output` | Output file | Print to stdout |
| `-m, --model` | Override model | From config |
| `-t, --temp` | Temperature (0.0-1.0) | 0.3 |

---

## 🛠️ Requirements

- Python 3.10+
- [Ollama](https://ollama.com) (installed automatically during onboard)

---

## 📝 License

MIT © 2026 CharlesArea

---

<div align="center">

**Made with ❤️ for the AI community**

[GitHub](https://github.com/CharlesArea/Redukon) • [PyPI](https://pypi.org/project/redukon/) • [Report Bug](https://github.com/CharlesArea/Redukon/issues)

</div>
