import json
import os
from typing import Dict, Any

def load_config(config_file: str = 'config.json') -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'model': 'llama-3.3-70b-versatile',
            'max_tokens': 2000,
            'max_messages': 20
        }

def get_api_key() -> str:
    """Get the Groq API key from environment variables."""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError(
            "Groq API key not found. Please set the GROQ_API_KEY environment variable.\n"
            "You can set it by running:\n"
            "set GROQ_API_KEY=your_api_key (Windows)\n"
            "or export GROQ_API_KEY=your_api_key (Linux/Mac)"
        )
    return api_key
