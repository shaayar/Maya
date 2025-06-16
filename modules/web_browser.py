import webbrowser
from urllib.parse import quote_plus
from typing import Optional

class WebBrowser:
    """Handles web browsing operations."""
    
    def __init__(self):
        self.default_search_engine = "https://www.google.com/search?q={}"
        self.supported_engines = {
            'google': 'https://www.google.com/search?q={}',
            'bing': 'https://www.bing.com/search?q={}',
            'duckduckgo': 'https://duckduckgo.com/?q={}',
            'youtube': 'https://www.youtube.com/results?search_query={}'
        }
    
    def search_web(self, query: str, engine: str = 'google') -> bool:
        """Search the web using the specified search engine."""
        engine_url = self.supported_engines.get(engine.lower(), self.default_search_engine)
        try:
            search_url = engine_url.format(quote_plus(query))
            return self.open_url(search_url)
        except Exception as e:
            print(f"Error performing web search: {e}")
            return False
    
    @staticmethod
    def open_url(url: str) -> bool:
        """Open a URL in the default web browser."""
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"Error opening URL {url}: {e}")
            return False
    
    def list_search_engines(self) -> list:
        """List all supported search engines."""
        return list(self.supported_engines.keys())
    
    def set_default_search_engine(self, engine: str) -> bool:
        """Set the default search engine."""
        if engine.lower() in self.supported_engines:
            self.default_search_engine = self.supported_engines[engine.lower()]
            return True
        return False
