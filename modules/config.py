import json
import os
from typing import Dict, Any, List

def load_config(config_file: str = 'config.json') -> Dict[str, Any]:
    """
    Load configuration from a JSON file with defaults.
    
    Args:
        config_file: Path to the config file
        
    Returns:
        Dict containing configuration with defaults for any missing values
    """
    # Default configuration
    default_config = {
        'model': 'llama-3.3-70b-versatile',
        'max_tokens': 2000,
        'max_messages': 20,
        'temperature': 0.7,
        'messages': [
            {
                'role': 'system',
                'content': 'You are a helpful AI assistant.'
            }
        ]
    }
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            
        # Merge user config with defaults
        for key, value in default_config.items():
            if key not in user_config:
                user_config[key] = value
                
        # Ensure messages list has at least one system message
        if not any(msg.get('role') == 'system' for msg in user_config.get('messages', [])):
            user_config['messages'] = default_config['messages'] + user_config.get('messages', [])
            
        return user_config
        
    except (FileNotFoundError, json.JSONDecodeError):
        # Return defaults if file doesn't exist or is invalid
        return default_config

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
