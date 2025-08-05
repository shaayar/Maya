"""
MCP (Model Control Protocol) Client for interacting with model endpoints.

This module provides an async client for making requests to MCP-compatible servers.
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, AsyncGenerator, Any, Union
import aiohttp
from aiohttp import ClientSession, ClientTimeout

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for interacting with MCP (Model Control Protocol) servers."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        timeout: float = 30.0,
        max_retries: int = 3,
        session: Optional[ClientSession] = None
    ):
        """
        Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            session: Optional aiohttp ClientSession to reuse
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = session
        self._endpoints = {
            'completions': '/v1/completions',
            'chat': '/v1/chat/completions',
            'models': '/v1/models'
        }
    
    async def __aenter__(self):
        if self._session is None:
            self._session = ClientSession(timeout=ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _get_url(self, endpoint: str) -> str:
        """Get the full URL for an endpoint."""
        return f"{self.base_url}{self._endpoints.get(endpoint, endpoint)}"
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """Get available models from the MCP server."""
        async with self._session.get(self._get_url('models')) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get('data', [])
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        Send a chat completion request to the MCP server.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model ID to use for completion
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Response from the MCP server or an async generator for streaming
        """
        url = self._get_url('chat')
        payload = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'stream': stream,
            **kwargs
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream' if stream else 'application/json'
        }
        
        if stream:
            return self._stream_request(url, payload, headers)
        else:
            return await self._request('POST', url, json=payload, headers=headers)
    
    async def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request with retries."""
        if self._session is None:
            async with ClientSession() as session:
                self._session = session
                return await self._do_request(method, url, **kwargs)
        return await self._do_request(method, url, **kwargs)
    
    async def _do_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the HTTP request with retries."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with self._session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = e
                logger.warning(
                    "Request failed (attempt %d/%d): %s",
                    attempt + 1, self.max_retries, str(e)
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception(f"Request failed after {self.max_retries} attempts: {last_error}")
    
    async def _stream_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle streaming response from the server."""
        session = self._session or ClientSession()
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                
                async for line in response.content:
                    if line.startswith(b'data: '):
                        data = line[6:].strip()
                        if data == b'[DONE]':
                            break
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse JSON: %s", data)
        finally:
            if session is not self._session and not session.closed:
                await session.close()

# Example usage:
# async def main():
#     async with MCPClient() as client:
#         # Get available models
#         models = await client.get_models()
#         print("Available models:", models)
#         
#         # Chat completion
#         response = await client.chat_completion(
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": "Hello!"}
#             ],
#             model="gpt-3.5-turbo"
#         )
#         print("Response:", response)
# 
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
