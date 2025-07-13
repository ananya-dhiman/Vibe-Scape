import requests
import json
import logging
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self, api_key: str = None, model: str = "anthropic/claude-3-haiku"):
        """
        Initialize OpenRouter client
        
        Args:
            api_key: OpenRouter API key (get from https://openrouter.ai/keys)
            model: Model to use (default: claude-3-haiku - fast and cheap)
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable or pass api_key parameter.")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        
    def generate_content(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """
        Generate content using OpenRouter API
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Generation temperature (0.0-1.0)
            
        Returns:
            Generated text response
        """
        try:
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Make request to OpenRouter
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 150,  # Limit for faster responses
                    "stream": False
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                logger.debug(f"OpenRouter response: {content[:100]}...")
                return content
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenRouter API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}")
            raise e
    
    def generate_json(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        Generate JSON response using OpenRouter
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            
        Returns:
            Parsed JSON response
        """
        try:
            # Add JSON formatting instruction
            json_prompt = f"{prompt}\n\nRespond with valid JSON only."
            
            response_text = self.generate_content(json_prompt, system_prompt, temperature=0.1)
            
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    logger.warning("No JSON found in response, attempting to parse full response")
                    return json.loads(response_text)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {response_text}")
                raise Exception(f"Invalid JSON response from OpenRouter: {e}")
                
        except Exception as e:
            logger.error(f"Error generating JSON with OpenRouter: {e}")
            raise e
    
    def batch_generate(self, prompts: List[str], system_prompt: str = None) -> List[str]:
        """
        Generate responses for multiple prompts in batch
        
        Args:
            prompts: List of prompts
            system_prompt: Optional system prompt
            
        Returns:
            List of generated responses
        """
        responses = []
        
        for i, prompt in enumerate(prompts):
            try:
                response = self.generate_content(prompt, system_prompt)
                responses.append(response)
                logger.info(f"Generated response {i+1}/{len(prompts)}")
            except Exception as e:
                logger.error(f"Error generating response {i+1}: {e}")
                responses.append("")  # Empty response on error
        
        return responses
    
    def health_check(self) -> bool:
        """
        Check if OpenRouter is accessible
        
        Returns:
            True if OpenRouter is healthy, False otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"OpenRouter health check failed: {e}")
            return False

# Global OpenRouter client instance
# You need to set your API key here or use environment variable
openrouter_client = OpenRouterClient() 