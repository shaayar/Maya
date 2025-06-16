import httpx
from typing import Optional, Dict, Any

class WebClient:
    """Handles all web-related operations."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or ""
        self.client = httpx.AsyncClient()
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making GET request to {url}: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
