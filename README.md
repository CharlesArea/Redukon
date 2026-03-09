# Redukon

A token-saving prompt rewriter using local small models (0.5b-4b). Runs entirely offline with Ollama - no API keys needed.

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# 1. Onboard - install Ollama and pick a model
redukon onboard

# 2. Rewrite a prompt
redukon rewrite -i "Your long prompt here..."

# 3. Or use a file
redukon rewrite -i @prompt.txt -o optimized.txt
```

## Commands

### `redukon onboard`
Interactive setup:
1. Checks if Ollama is installed
2. If not, prompts to install
3. Lets you choose a model:
   - qwen2.5:0.5b (smallest, fastest)
   - qwen2.5:0.8b
   - llama3.2:1b
   - phi3:3.8b

Saves config to `~/.redukon/config.json`

### `redukon rewrite`
Rewrite a prompt locally.

**Options:**
- `-i, --input` - Prompt string or `@file.txt` for file input
- `-o, --output` - Output file (optional, prints to stdout if not set)
- `-m, --model` - Override model
- `-t, --temp` - Temperature (default: 0.3)

**Examples:**
```bash
# String input
redukon rewrite -i "Please write a function that adds two numbers"

# File input
redukon rewrite -i @long_prompt.txt

# With output file
redukon rewrite -i @prompt.txt -o optimized.txt

# Override model
redukon rewrite -i "prompt" -m qwen2.5:0.8b
```

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com) - installed automatically during onboard

## License

MIT
