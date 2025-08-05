import json
import os
from typing import Dict, Any, List, Optional

# Default configuration
DEFAULT_CONFIG = {
    # Model configuration
    'model': 'llama-3.3-70b-versatile',
    'max_tokens': 2000,
    'max_messages': 20,
    'temperature': 0.7,
    'messages': [
        {
            'role': 'system',
            'content': 'You are Maya, a helpful AI assistant.'
        }
    ],
    
    # MCP (Model Control Protocol) configuration
    'mcp': {
        'enabled': False,
        'base_url': 'http://localhost:8080',
        'endpoints': {
            'completions': '/v1/completions',
            'chat': '/v1/chat/completions',
            'models': '/v1/models'
        },
        'timeout': 30.0,
        'max_retries': 3,
        'default_model': 'gpt-3.5-turbo'
    },
    
    # UI settings
    'ui': {
        'theme': 'system',  # 'light', 'dark', or 'system'
        'font_size': 12,
        'font_family': 'Arial, sans-serif'
    }
}

def deep_merge(base: Dict, update: Dict) -> Dict:
    """Recursively merge two dictionaries."""
    result = base.copy()
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def load_config(config_file: str = 'config.json') -> Dict[str, Any]:
    """
    Load configuration from a JSON file with defaults.
    
    Args:
        config_file: Path to the config file
        
    Returns:
        Dict containing configuration with defaults for any missing values
    """
    # Start with default configuration
    config = DEFAULT_CONFIG.copy()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            
        # Deep merge user config with defaults
        config = deep_merge(config, user_config)
        
        # Ensure messages list has at least one system message
        if not any(msg.get('role') == 'system' for msg in config.get('messages', [])):
            config['messages'] = DEFAULT_CONFIG['messages'] + config.get('messages', [])
            
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if isinstance(e, json.JSONDecodeError):
            print(f"Warning: Invalid JSON in config file: {e}")
        # Continue with default config
    
    return config

def get_api_key(service: str = 'groq') -> Optional[str]:
    """
    Get API key from environment variables.
    
    Args:
        service: Service name (e.g., 'groq', 'openai')
        
    Returns:
        API key or None if not found
    """
    env_var = f"{service.upper()}_API_KEY"
    return os.getenv(env_var)

def save_config(config: Dict[str, Any], config_file: str = 'config.json') -> None:
    """
    Save configuration to a JSON file.
    
    Args:
        config: Configuration dictionary to save
        config_file: Path to the config file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def update_config(updates: Dict[str, Any], config_file: str = 'config.json') -> Dict[str, Any]:
    """
    Update configuration with new values and save to file.
    
    Args:
        updates: Dictionary with configuration updates
        config_file: Path to the config file
        
    Returns:
        Updated configuration
    """
    config = load_config(config_file)
    config = deep_merge(config, updates)
    save_config(config, config_file)
    return config
