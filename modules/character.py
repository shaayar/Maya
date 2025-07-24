"""
Character system for MAYA AI Chatbot.
Handles anime character traits and voice customization.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
from pathlib import Path

@dataclass
class CharacterTrait:
    """Represents a character trait with voice and response modifications."""
    name: str
    description: str
    pitch_modifier: float = 0.0  # -1.0 to 1.0
    speed_modifier: float = 1.0  # 0.5 to 2.0
    response_style: str = "neutral"  # neutral, formal, casual, tsundere, etc.
    keywords: List[str] = field(default_factory=list)  # Words that trigger special responses

class CharacterSystem:
    """Manages anime character traits and voice customization."""
    
    def __init__(self, config_path: str = "config/character.json"):
        """Initialize the character system with default or saved traits."""
        self.config_path = Path(config_path)
        self.default_traits = self._get_default_traits()
        self.current_traits = self._load_traits()
        
    def _get_default_traits(self) -> Dict[str, CharacterTrait]:
        """Return default character traits."""
        return {
            "tsundere": CharacterTrait(
                name="Tsundere",
                description="Acts cold but has a warm heart",
                pitch_modifier=0.5,
                speed_modifier=1.2,
                response_style="tsundere",
                keywords=["baka", "idiot", "whatever", "it's not like I like you or anything"]
            ),
            "kuudere": CharacterTrait(
                name="Kuudere",
                description="Calm and collected, shows little emotion",
                pitch_modifier=0.0,
                speed_modifier=0.9,
                response_style="kuudere",
                keywords=["...", "I see", "Understood"]
            ),
            "genki": CharacterTrait(
                name="Genki",
                description="Energetic and cheerful",
                pitch_modifier=0.8,
                speed_modifier=1.5,
                response_style="genki",
                keywords=["yay!", "let's go!", "so exciting!"]
            )
        }
    
    def _load_traits(self) -> Dict[str, CharacterTrait]:
        """Load traits from config file or create default if not exists."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {k: CharacterTrait(**v) for k, v in data.items()}
        except Exception as e:
            print(f"Error loading character traits: {e}")
        
        # Return default traits if loading fails
        return self.default_traits
    
    def save_traits(self) -> bool:
        """Save current traits to config file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(
                    {k: v.__dict__ for k, v in self.current_traits.items()},
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            return True
        except Exception as e:
            print(f"Error saving character traits: {e}")
            return False
    
    def get_available_traits(self) -> List[str]:
        """Return list of available trait names."""
        return list(self.default_traits.keys())
    
    def set_character_trait(self, trait_name: str) -> bool:
        """Set the current character trait."""
        if trait_name in self.default_traits:
            self.current_traits[trait_name] = self.default_traits[trait_name]
            return True
        return False
    
    def get_current_trait(self) -> Optional[CharacterTrait]:
        """Get the current character trait."""
        if self.current_traits:
            return next(iter(self.current_traits.values()))
        return None
    
    def customize_trait(self, trait_name: str, **kwargs) -> bool:
        """Customize an existing trait or create a new one."""
        if trait_name in self.default_traits:
            trait = self.default_traits[trait_name]
            for key, value in kwargs.items():
                if hasattr(trait, key):
                    setattr(trait, key, value)
            self.current_traits[trait_name] = trait
            return True
        return False

    def format_response(self, text: str) -> str:
        """Format a response according to the current character's style."""
        trait = self.get_current_trait()
        if not trait:
            return text
            
        if trait.response_style == "tsundere":
            return f"B-baka! {text} It's not like I wanted to tell you that or anything..."
        elif trait.response_style == "kuudere":
            return f"{text}..."
        elif trait.response_style == "genki":
            return f"Yay! {text.upper()}! Let's do our best! ☆⌒(≧▽° )"
        return text
