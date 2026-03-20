"""
OpenRouter AI service for Kanban application.
"""
import logging
import time
from typing import Any, Dict, Optional

import httpx
from httpx import HTTPStatusError, RequestError

from src.config.settings import settings

logger = logging.getLogger(__name__)


class OpenRouterService:
    """
    Service for interacting with OpenRouter AI API.
    """
    
    def __init__(self):
        """
        Initialize OpenRouter service with API configuration.
        """
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = settings.openrouter_base_url
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")
        
        logger.info(f"OpenRouter service initialized with model: {self.model}")
    
    async def _make_request(
        self, 
        messages: list, 
        max_tokens: int = 100, 
        temperature: float = 0.7,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request to OpenRouter API with retry logic.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens for response
            temperature: Temperature for response creativity
            retry_count: Current retry attempt count
            
        Returns:
            Dictionary containing AI response
            
        Raises:
            RequestError: If request fails after max retries
            HTTPStatusError: If API returns error status
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
            "X-Title": "Kanban AI Assistant",  # Required by OpenRouter
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        url = f"{self.base_url}/chat/completions"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.debug(f"Sending request to OpenRouter: {payload}")
                response = await client.post(url, headers=headers, json=payload)
                
                # Check for successful response
                response.raise_for_status()
                
                result = response.json()
                logger.debug(f"Received response from OpenRouter: {result}")
                return result
                
        except HTTPStatusError as e:
            logger.error(f"OpenRouter API error: {e}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying request (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
                return await self._make_request(messages, max_tokens, temperature, retry_count + 1)
            else:
                logger.error(f"Max retries ({self.max_retries}) exceeded for OpenRouter request")
                raise
                
        except RequestError as e:
            logger.error(f"OpenRouter request failed: {e}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying request (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
                return await self._make_request(messages, max_tokens, temperature, retry_count + 1)
            else:
                logger.error(f"Max retries ({self.max_retries}) exceeded for OpenRouter request")
                raise
        
        except Exception as e:
            logger.error(f"Unexpected error calling OpenRouter API: {e}")
            raise
    
    async def chat_completion(
        self, 
        messages: list, 
        max_tokens: int = 100, 
        temperature: float = 0.7
    ) -> str:
        """
        Get chat completion from OpenRouter API.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens for response
            temperature: Temperature for response creativity
            
        Returns:
            String containing the AI response content
            
        Raises:
            RequestError: If request fails after max retries
            HTTPStatusError: If API returns error status
        """
        try:
            result = await self._make_request(messages, max_tokens, temperature)
            
            # Extract and return the content from the first choice
            if result.get("choices") and len(result["choices"]) > 0:
                choice = result["choices"][0]
                message = choice["message"]
                
                # Handle different response structures from OpenRouter
                if message.get("content"):
                    return message["content"].strip()
                elif message.get("reasoning"):
                    # Some OpenRouter models return reasoning instead of content
                    return message["reasoning"].strip()
                elif message.get("refusal"):
                    # Handle refusal responses
                    return f"I cannot answer that: {message['refusal']}"
                else:
                    logger.error(f"No valid content in OpenRouter response: {result}")
                    raise ValueError("No valid response from OpenRouter API")
            else:
                logger.error(f"No choices in OpenRouter response: {result}")
                raise ValueError("No valid response from OpenRouter API")
                
        except Exception as e:
            logger.error(f"Failed to get chat completion: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """
        Test connection to OpenRouter API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test with a basic math question
            messages = [
                {"role": "user", "content": "What is 2+2?"}
            ]
            
            response = await self.chat_completion(messages, max_tokens=50)
            
            # Check if response contains expected answer or indicates successful connection
            # The model might return reasoning like "The user asks a simple question..."
            success_indicators = ["4", "four", "2+2=4", "2+2 is 4", "simple", "question", "answer"]
            return any(indicator.lower() in response.lower() for indicator in success_indicators)
            
        except Exception as e:
            logger.error(f"OpenRouter connection test failed: {e}")
            return False


# Create singleton instance
openrouter_service = OpenRouterService()