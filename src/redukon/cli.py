"""Redukon CLI - Simple token-saving prompt rewriter."""

import os
import json
import click
from pathlib import Path
from .ollama import check_installed, install, list as list_models, pull, generate
from .api import run_server

CONFIG_DIR = Path.home() / ".redukon"
CONFIG_FILE = CONFIG_DIR / "config.json"

MODELS = ["qwen2.5:0.5b", "llama3.2:1b", "phi3:3.8b"]

DEFAULT_SYSTEM_PROMPT = """You are a prompt optimizer. Your goal is to make prompts CONCISE while keeping the core intent.

RULES:
1. Remove filler words and redundant phrases
2. Combine sentences where possible
3. Keep key requirements and constraints
4. Use shorter synonyms
5. Output ONLY the optimized prompt - no explanations, no code, no comments

Example:
Input: "Can you please help me create a Python function that takes a list of numbers as input and returns the sum of all even numbers in that list? It would be great if you could also include proper error handling."
Output: "Create a Python function that takes a list of numbers and returns the sum of even numbers. Include error handling." """


def load_config():
    """Load config from ~/.redukon/config.json"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(config):
    """Save config to ~/.redukon/config.json"""
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_system_prompt(config):
    """Get system prompt from config or use default."""
    return config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)


@click.group()
def cli():
    """Redukon - Token-saving prompt rewriter using local small models."""
    pass


@cli.command()
def onboard():
    """Onboard: check/install Ollama and select a model."""
    click.echo("🚀 Welcome to Redukon!")

    # Check Ollama
    if not check_installed():
        click.echo("\n❌ Ollama is not installed.")
        if click.confirm("Install Ollama now? (y/n)"):
            click.echo("\n📦 Installing Ollama...")
            install()
            click.echo("✅ Ollama installed!")
        else:
            click.echo("\n👋 Run 'redukon onboard' later when ready.")
            return
    else:
        click.echo("✅ Ollama is installed!")

    # List available models
    click.echo("\n📋 Available models:")
    for i, m in enumerate(MODELS, 1):
        click.echo(f"  {i}. {m}")

    # Select model
    choice = click.prompt("\nSelect a model (1-4)", type=int, default=1)
    if 1 <= choice <= len(MODELS):
        model = MODELS[choice - 1]
    else:
        model = MODELS[0]

    # Select temperature
    temp = click.prompt(
        "\nEnter temperature (0.0-1.0, lower = more focused)", type=float, default=0.3
    )

    # Save config
    config = {
        "model": model,
        "temperature": temp,
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
    }
    save_config(config)
    click.echo(f"\n✅ Saved: model={model}, temp={temp}")
    click.echo("🎉 Onboard complete! Run 'redukon rewrite -i \"your prompt\"'")
    click.echo("\n💡 Tip: Run 'redukon config' to view or edit your system prompt.")


@cli.command("config")
def config_cmd():
    """View or edit configuration."""
    config = load_config()

    if not config:
        click.echo("❌ No config found. Run 'redukon onboard' first.")
        return

    click.echo("\n📋 Current Config:")
    click.echo(f"  Model:      {config.get('model', 'Not set')}")
    click.echo(f"  Temperature: {config.get('temperature', 0.3)}")

    # Show system prompt preview
    sp = config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
    click.echo(f"\n📝 System Prompt (first 200 chars):")
    click.echo(f"  {sp[:200]}...")

    # Edit options
    click.echo("\n🔧 Edit options:")
    click.echo("  1. Edit system prompt")
    click.echo("  2. Change temperature")
    click.echo("  3. Change model")
    click.echo("  4. Reset to defaults")
    click.echo("  0. Exit")

    choice = click.prompt("\nSelect (0-4)", type=int, default=0)

    if choice == 1:
        click.echo(
            "\n📝 Enter new system prompt (press Enter on empty line to finish):"
        )
        lines = []
        while True:
            line = click.prompt("", default="", show_default=False)
            if line == "":
                break
            lines.append(line)
        new_prompt = "\n".join(lines)
        if new_prompt.strip():
            config["system_prompt"] = new_prompt
            save_config(config)
            click.echo("✅ System prompt updated!")
    elif choice == 2:
        temp = click.prompt(
            "Enter temperature (0.0-1.0)",
            type=float,
            default=config.get("temperature", 0.3),
        )
        config["temperature"] = temp
        save_config(config)
        click.echo(f"✅ Temperature set to {temp}")
    elif choice == 3:
        click.echo("\n📋 Available models:")
        for i, m in enumerate(MODELS, 1):
            click.echo(f"  {i}. {m}")
        choice = click.prompt("Select model (1-4)", type=int, default=1)
        if 1 <= choice <= len(MODELS):
            config["model"] = MODELS[choice - 1]
            save_config(config)
            click.echo(f"✅ Model set to {MODELS[choice - 1]}")
    elif choice == 4:
        config["system_prompt"] = DEFAULT_SYSTEM_PROMPT
        save_config(config)
        click.echo("✅ Reset to defaults!")


@cli.command()
@click.option(
    "-i", "--input", "input_", required=True, help="Prompt string or @file.txt"
)
@click.option("-o", "--output", help="Output file (optional)")
@click.option("-m", "--model", help="Override model (e.g., qwen2.5:0.5b)")
@click.option("-t", "--temp", "temperature", type=float, help="Override temperature")
def rewrite(input_, output, model, temperature):
    """Rewrite a prompt to save tokens."""
    # Load config
    config = load_config()

    if not config:
        click.echo("❌ Not onboarded yet. Run 'redukon onboard' first.")
        return

    # Resolve input
    prompt = input_
    if input_.startswith("@"):
        file_path = Path(input_[1:])
        if file_path.exists():
            prompt = file_path.read_text().strip()
        else:
            click.echo(f"❌ File not found: {file_path}")
            return

    # Use model/temp from args or config
    model = model or config.get("model")
    temp = temperature if temperature is not None else config.get("temperature", 0.3)
    system_prompt = get_system_prompt(config)

    click.echo(f"🔄 Rewriting with {model} (temp={temp})...")

    # Generate
    result = generate(model, prompt, temperature=temp, system_prompt=system_prompt)

    if result:
        if output:
            Path(output).write_text(result)
            click.echo(f"✅ Saved to {output}")
        else:
            click.echo("\n" + result)

        # Stats
        orig_tokens = len(prompt) // 4
        new_tokens = len(result) // 4
        saved = orig_tokens - new_tokens
        if saved > 0 and orig_tokens > 0:
            click.echo(f"📉 Saved ~{saved} tokens ({saved * 100 // orig_tokens}%)")
    else:
        click.echo("❌ Failed to generate response.")


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
def serve(host, port):
    """Start the API server."""
    click.echo(f"🚀 Starting Redukon API server on {host}:{port}")
    click.echo("📋 Endpoints:")
    click.echo("  POST /rewrite - Rewrite a prompt")
    click.echo("  GET  /health  - Health check")
    click.echo("\n📝 Example request:")
    click.echo(
        '  curl -X POST http://localhost:8000/rewrite -H "Content-Type: application/json" -d \'{"prompt": "Your prompt here", "model": "qwen2.5:0.5b", "temperature": 0.3}\''
    )
    run_server(host=host, port=port)


if __name__ == "__main__":
    cli()


def main():
    """Entry point for CLI."""
    cli()
