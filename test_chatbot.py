import sys
import os
from modules.config import load_config
from modules.chatbot import Chatbot

def test_chatbot():
    print("Testing Chatbot with updated configuration...")
    
    # Load the config
    config = load_config()
    print("\nLoaded configuration:")
    for key, value in config.items():
        if key != 'messages':
            print(f"{key}: {value}")
    print("System messages:")
    for msg in config.get('messages', []):
        if msg.get('role') == 'system':
            print(f"- {msg.get('content')}")
    
    # Initialize the chatbot
    try:
        print("\nInitializing chatbot...")
        chatbot = Chatbot(config)
        
        # Test a simple conversation
        print("\nStarting conversation...")
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            response = chatbot.get_response(user_input)
            print(f"\nMAYA: {response}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_chatbot()
