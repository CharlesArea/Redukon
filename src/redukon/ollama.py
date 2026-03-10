import subprocess
import requests
import os


def check_installed():
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install():
    install_script = """curl -fsSL https://ollama.com/install.sh | sh"""
    subprocess.run(["bash", "-c", install_script], check=True)


def list():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode != 0:
            return []
        lines = result.stdout.strip().split("\n")[1:]
        models = []
        for line in lines:
            if line.strip():
                parts = line.split()
                if parts:
                    models.append(parts[0])
        return models
    except Exception:
        return []


def pull(model_name):
    result = subprocess.run(
        ["ollama", "pull", model_name], capture_output=True, text=True
    )
    return result.returncode == 0


def generate(model_name, prompt, temperature=0.7, system_prompt=None):
    url = "http://localhost:11434/api/generate"
    
    # Use provided system prompt or default
    if system_prompt is None:
        system_prompt = """You are a prompt optimizer. Your goal is to make prompts CONCISE while keeping the core intent.

RULES:
1. Remove filler words and redundant phrases
2. Combine sentences where possible
3. Keep key requirements and constraints
4. Use shorter synonyms
5. Output ONLY the optimized prompt - no explanations, no code, no comments

Example:
Input: "Can you please help me create a Python function that takes a list of numbers as input and returns the sum of all even numbers in that list? It would be great if you could also include proper error handling."
Output: "Create a Python function that takes a list of numbers and returns the sum of even numbers. Include error handling." """
    
    full_prompt = f"{system_prompt}\n\nOptimize this prompt: {prompt}\n\nOutput:"
    
    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "")
    return None


def generate_stream(model_name, prompt, temperature=0.7, system_prompt=None):
    """Generate with streaming - yields tokens as they come."""
    url = "http://localhost:11434/api/generate"
    
    if system_prompt is None:
        system_prompt = """You are a prompt optimizer. Your goal is to make prompts CONCISE while keeping the core intent.

RULES:
1. Remove filler words and redundant phrases
2. Combine sentences where possible
3. Keep key requirements and constraints
4. Use shorter synonyms
5. Output ONLY the optimized prompt - no explanations, no code, no comments

Example:
Input: "Can you please help me create a Python function that takes a list of numbers as input and returns the sum of all even numbers in that list? It would be great if you could also include proper error handling."
Output: "Create a Python function that takes a list of numbers and returns the sum of even numbers. Include error handling." """
    
    full_prompt = f"{system_prompt}\n\nOptimize this prompt: {prompt}\n\nOutput:"
    
    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "stream": True,
        "options": {"temperature": temperature},
    }
    
    response = requests.post(url, json=payload, stream=True)
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                if data.startswith('data:'):
                    import json
                    try:
                        chunk = json.loads(data[5:])
                        if 'response' in chunk:
                            yield chunk['response']
                    except:
                        pass
    return None
