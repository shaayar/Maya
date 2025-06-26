from typing import List, Dict, Any, Optional
from groq import Groq
from .config import get_api_key

class Chatbot:
    """Handles chat functionality with Groq API."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the chatbot with configuration.
        
        Args:
            config: Dictionary containing configuration including:
                   - model: The model to use
                   - max_tokens: Maximum tokens per response
                   - temperature: Sampling temperature (0.0 to 1.0)
                   - messages: List of message dictionaries with role and content
        """
        self.config = config
        self.client = Groq(api_key=get_api_key())
        
        # Initialize messages with system message from config or default
        self.messages = config.get('messages', [
            {
                "role": "system",
                "content": "You are MAYA, a helpful AI assistant. Keep your responses concise and to the point."
            }
        ])
        
        # Ensure we have at least one system message
        if not any(msg.get('role') == 'system' for msg in self.messages):
            self.messages.insert(0, {
                "role": "system",
                "content": "You are MAYA, a helpful AI assistant."
            })
            
        self.conversation_history = []
    
    def get_response(self, user_input: str) -> str:
        """Get a response from the chatbot."""
        # Add user message to conversation history
        self.messages.append({"role": "user", "content": user_input})
        
        # Prepare the conversation context
        context_messages = [self.messages[0]]  # Start with system message
        
        # Add recent messages, keeping within token limit
        max_context_messages = min(10, len(self.messages) - 1)
        context_messages.extend(self.messages[-max_context_messages:])
        
        try:
            # Get response from Groq
            response = self.client.chat.completions.create(
                messages=context_messages,
                model=self.config.get('model', 'llama-3.3-70b-versatile'),
                max_tokens=self.config.get('max_tokens', 2000),
                temperature=float(self.config.get('temperature', 0.7)),
                stream=False
            )
            
            ai_response = response.choices[0].message.content
            
            # Add assistant's response to messages
            self.messages.append({"role": "assistant", "content": ai_response})
            
            # Store complete conversation history
            self.conversation_history.append(("user", user_input))
            self.conversation_history.append(("assistant", ai_response))
            
            # Trim messages if they exceed the maximum allowed
            if len(self.messages) > self.config['max_messages'] + 1:  # +1 for system message
                self.messages = [self.messages[0]] + self.messages[-self.config['max_messages']:]
            
            return ai_response
            
        except Exception as e:
            raise Exception(f"Error getting response from Groq: {str(e)}")
    
    def clear_conversation(self):
        """Clear the conversation history while keeping the system message."""
        self.messages = [self.messages[0]]  # Keep only the system message
        self.conversation_history = []
