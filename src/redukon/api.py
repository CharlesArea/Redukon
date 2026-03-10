import os
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, Response
from .ollama import generate, generate_stream
from .cli import load_config, get_system_prompt, DEFAULT_SYSTEM_PROMPT

app = Flask(__name__)

LOG_DIR = Path("log")
LOG_DIR.mkdir(exist_ok=True)


def get_logger():
    """Get a date-based logger."""
    log_file = LOG_DIR / f"api-{datetime.now().strftime('%Y-%m-%d')}.log"
    return log_file


def log_request(level, message):
    """Log a message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}\n"
    with open(get_logger(), "a") as f:
        f.write(log_line)


def count_tokens(text):
    """Estimate token count (roughly 4 chars per token)."""
    return len(text) // 4


@app.route("/rewrite", methods=["POST"])
def rewrite():
    """Rewrite endpoint - non-streaming."""
    try:
        data = request.get_json()

        if not data:
            log_request("ERROR", "No JSON body provided")
            return jsonify({"error": "No JSON body provided"}), 400

        prompt = data.get("prompt")
        if not prompt:
            log_request("ERROR", "Missing required field: prompt")
            return jsonify({"error": "Missing required field: prompt"}), 400

        model = data.get("model")
        temperature = data.get("temperature")

        config = load_config()

        if not model:
            model = config.get("model", "qwen2.5:0.5b")
        if temperature is None:
            temperature = config.get("temperature", 0.3)

        system_prompt = get_system_prompt(config) if config else DEFAULT_SYSTEM_PROMPT

        original_tokens = count_tokens(prompt)
        log_request("REQUEST", f"input_length={len(prompt)}, model={model}, stream=false")

        try:
            optimized_prompt = generate(
                model, prompt, temperature=temperature, system_prompt=system_prompt
            )
        except Exception as e:
            log_request("ERROR", f"Generation failed: {str(e)}")
            return jsonify({"error": f"Generation failed: {str(e)}"}), 500

        if not optimized_prompt:
            log_request("ERROR", "Failed to generate response from model")
            return jsonify({"error": "Failed to generate response from model"}), 500

        optimized_tokens = count_tokens(optimized_prompt)
        saved_tokens = original_tokens - optimized_tokens
        saved_percent = int(
            (saved_tokens / original_tokens * 100) if original_tokens > 0 else 0
        )

        log_request(
            "RESPONSE",
            f"output_length={len(optimized_prompt)}, original_tokens={original_tokens}, optimized_tokens={optimized_tokens}, saved_tokens={saved_tokens}, saved_percent={saved_percent}%",
        )

        return jsonify(
            {
                "optimized_prompt": optimized_prompt,
                "original_tokens": original_tokens,
                "optimized_tokens": optimized_tokens,
                "saved_tokens": saved_tokens,
                "saved_percent": saved_percent,
            }
        )

    except Exception as e:
        log_request("ERROR", f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/rewrite/stream", methods=["POST"])
def rewrite_stream():
    """Rewrite endpoint with streaming."""
    try:
        data = request.get_json()

        if not data:
            log_request("ERROR", "No JSON body provided")
            return jsonify({"error": "No JSON body provided"}), 400

        prompt = data.get("prompt")
        if not prompt:
            log_request("ERROR", "Missing required field: prompt")
            return jsonify({"error": "Missing required field: prompt"}), 400

        model = data.get("model")
        temperature = data.get("temperature")

        config = load_config()

        if not model:
            model = config.get("model", "qwen2.5:0.5b")
        if temperature is None:
            temperature = config.get("temperature", 0.3)

        system_prompt = get_system_prompt(config) if config else DEFAULT_SYSTEM_PROMPT

        original_tokens = count_tokens(prompt)
        log_request("REQUEST", f"input_length={len(prompt)}, model={model}, stream=true")

        def generate_sse():
            full_response = ""
            try:
                for chunk in generate_stream(model, prompt, temperature, system_prompt):
                    if chunk:
                        full_response += chunk
                        # Send as SSE (Server-Sent Events)
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Send final stats
                optimized_tokens = count_tokens(full_response)
                saved_tokens = original_tokens - optimized_tokens
                saved_percent = int(
                    (saved_tokens / original_tokens * 100) if original_tokens > 0 else 0
                )
                
                log_request(
                    "RESPONSE",
                    f"output_length={len(full_response)}, original_tokens={original_tokens}, optimized_tokens={optimized_tokens}, saved_tokens={saved_tokens}, saved_percent={saved_percent}%",
                )
                
                yield f"data: {json.dumps({'done': True, 'original_tokens': original_tokens, 'optimized_tokens': optimized_tokens, 'saved_tokens': saved_tokens, 'saved_percent': saved_percent})}\n\n"
                
            except Exception as e:
                log_request("ERROR", f"Stream generation failed: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(
            generate_sse(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no-cache',
            }
        )

    except Exception as e:
        log_request("ERROR", f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/batch", methods=["POST"])
def batch():
    """Batch rewrite multiple prompts."""
    try:
        data = request.get_json()

        if not data:
            log_request("ERROR", "No JSON body provided")
            return jsonify({"error": "No JSON body provided"}), 400

        prompts = data.get("prompts")
        if not prompts or not isinstance(prompts, list):
            log_request("ERROR", "Missing or invalid 'prompts' field (must be a list)")
            return jsonify({"error": "Missing or invalid 'prompts' field (must be a list)"}), 400

        model = data.get("model")
        temperature = data.get("temperature")

        config = load_config()

        if not model:
            model = config.get("model", "qwen2.5:0.5b")
        if temperature is None:
            temperature = config.get("temperature", 0.3)

        system_prompt = get_system_prompt(config) if config else DEFAULT_SYSTEM_PROMPT

        log_request("BATCH", f"count={len(prompts)}, model={model}")

        results = []
        total_saved = 0
        total_original = 0

        for i, prompt in enumerate(prompts):
            try:
                optimized = generate(model, prompt, temperature=temperature, system_prompt=system_prompt)
                
                orig_tokens = count_tokens(prompt)
                new_tokens = count_tokens(optimized) if optimized else 0
                saved = orig_tokens - new_tokens
                
                results.append({
                    "index": i,
                    "original": prompt,
                    "optimized_prompt": optimized,
                    "original_tokens": orig_tokens,
                    "optimized_tokens": new_tokens,
                    "saved_tokens": saved,
                    "saved_percent": int((saved / orig_tokens * 100) if orig_tokens > 0 else 0)
                })
                
                total_saved += saved
                total_original += orig_tokens
                
            except Exception as e:
                results.append({
                    "index": i,
                    "original": prompt,
                    "error": str(e)
                })

        overall_percent = int(total_saved / total_original * 100) if total_original > 0 else 0
        
        log_request("BATCH", f"completed={len(results)}, total_saved={total_saved}, overall_percent={overall_percent}%")

        return jsonify({
            "results": results,
            "summary": {
                "total": len(prompts),
                "processed": len(results),
                "total_original_tokens": total_original,
                "total_saved_tokens": total_saved,
                "overall_saved_percent": overall_percent
            }
        })

    except Exception as e:
        log_request("ERROR", f"Batch error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


def run_server(host="0.0.0.0", port=8000):
    """Run the Flask server."""
    log_request("INFO", f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=False)
