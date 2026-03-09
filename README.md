# 🔥 Redukon

### Reduce Your Tokens. Keep Your Intent.

<p align="center">
  <img src="https://img.shields.io/pypi/v/redukon?color=%23ff6b6b&style=flat-square" alt="PyPI">
  <img src="https://img.shields.io/pypi/l/redukon?color=%23ff6b6b&style=flat-square" alt="License">
  <img src="https://img.shields.io/pypi/pyversions/redukon?color=%23ff6b6b&style=flat-square" alt="Python">
</p>

---

## ✨ What is Redukon?

Redukon is a **token-saving prompt rewriter** that uses local small AI models to optimize your prompts — reducing token count while keeping the core intent intact.

**No API keys needed.** Runs entirely offline with [Ollama](https://ollama.com).

💡 **Perfect for:**
- Saving money on API calls
- Fitting more context into LLM windows
- Making prompts more efficient

---

## 🚀 Quick Start

```bash
# Install
pip install -e .

# One-time setup (installs Ollama + picks a model)
redukon onboard

# Rewrite prompts to save tokens!
redukon rewrite -i "Your long prompt here..."
```

---

## 📖 Usage

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
Rewrite your prompts!

```bash
# Basic
redukon rewrite -i "Please write a comprehensive Python function..."

# From file
redukon rewrite -i @long-prompt.txt -o optimized.txt

# Custom temperature (lower = more focused)
redukon rewrite -i "prompt" --temp 0.3
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

##

- Python  🛠️ Requirements3.8+
- [Ollama](https://ollama.com) (installed automatically)

---

## 📝 License

MIT © 2026 CharlesArea

---

<div align="center">

**Made with ❤️ for the AI community**

[GitHub](https://github.com/CharlesArea/Redukon) • [Report Bug](https://github.com/CharlesArea/Redukon/issues)

</div>
