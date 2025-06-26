import sys
import os
import json
from modules.config import load_config

def test_config_loading():
    print("Testing config loading...")
    
    # Test 1: Load with default config
    print("\nTest 1: Loading with default config")
    config = load_config("non_existent_config.json")
    print("Default config loaded:")
    print(json.dumps(config, indent=2))
    
    # Test 2: Load with custom config
    print("\nTest 2: Loading with custom config")
    test_config = {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.8,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello!"}
        ]
    }
    
    with open("test_config.json", "w", encoding="utf-8") as f:
        json.dump(test_config, f)
    
    config = load_config("test_config.json")
    print("Custom config loaded:")
    print(json.dumps(config, indent=2))
    
    # Clean up
    try:
        os.remove("test_config.json")
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    test_config_loading()
