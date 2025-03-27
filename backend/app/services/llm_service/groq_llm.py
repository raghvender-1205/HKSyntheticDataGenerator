import aiohttp
from typing import List, Dict, Any
import json

from app.services.base import BaseLLMService
from app.models import DatasetType
from app.services.llm_service.prompts import get_base_prompt, get_dataset_specific_prompt


class GroqLLMService(BaseLLMService):
    def __init__(self, config: Dict):
        super().__init__(config)
        # Handle config as dictionary
        if isinstance(config, dict):
            self.api_key = config.get('api_key', '')
            self.model_name = config.get('model_name', 'llama3-8b-8192')
            self.api_base = config.get('api_base', 'https://api.groq.com/openai/v1')
            self.parameters = config.get('parameters', {}) or {}
        else:
            # Fallback for object-style config
            self.api_key = getattr(config, 'api_key', '')
            self.model_name = getattr(config, 'model_name', 'llama3-8b-8192')
            self.api_base = getattr(config, 'api_base', 'https://api.groq.com/openai/v1')
            self.parameters = getattr(config, 'parameters', {}) or {}

    async def generate_synthetic_data(
        self,
        base_data: List[Dict],
        sample_size: int,
        dataset_type: DatasetType
    ) -> List[Dict]:
        try:
            # Prepare prompt
            prompt = self._create_prompt(base_data, dataset_type, sample_size)
            
            # Extract generation parameters with defaults
            temperature = float(self.parameters.get("temperature", 0.7))
            max_tokens = int(self.parameters.get("max_tokens", 1000))
            
            # Configure generation parameters for chat completions
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a synthetic data generator assistant that creates high-quality, diverse examples based on provided samples."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Add optional parameters if provided
            if "top_p" in self.parameters:
                payload["top_p"] = float(self.parameters.get("top_p"))
            
            # Set up headers with API key
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Generate results
            results = []
            async with aiohttp.ClientSession() as session:
                for _ in range(sample_size):
                    # Make API request to Groq
                    async with session.post(
                        f"{self.api_base}/chat/completions",
                        json=payload,
                        headers=headers
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(f"Groq API error: {response.status}, {error_text}")
                        
                        result = await response.json()
                        # Extract text from response
                        generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        # Format the text based on dataset type
                        formatted_result = self._format_generated_text(generated_text, dataset_type)
                        results.append(formatted_result)
            
            return results
        
        except Exception as e:
            # Log the error and re-raise
            print(f"Error in Groq LLM service: {str(e)}")
            raise

    def _create_prompt(self, base_data: List[Dict], dataset_type: DatasetType, sample_size: int) -> str:
        base_prompt = get_base_prompt(base_data, dataset_type, sample_size)
        return get_dataset_specific_prompt(base_prompt, dataset_type)

    def _format_response(self, result: Dict, dataset_type: DatasetType) -> List[Dict]:
        """
        Format the API response into the expected output format
        This method is required by the BaseLLMService abstract class
        """
        if not result or "choices" not in result:
            return []
        
        formatted_results = []
        for choice in result.get("choices", []):
            if "message" in choice and "content" in choice["message"]:
                text = choice["message"]["content"]
                formatted_result = self._format_generated_text(text, dataset_type)
                formatted_results.append(formatted_result)
        
        return formatted_results

    def _format_generated_text(self, text: str, dataset_type: DatasetType) -> Dict:
        """Format the generated text based on the dataset type"""
        try:
            # Try to parse as JSON
            data = json.loads(text)
            return data
        except json.JSONDecodeError:
            # If not valid JSON, use simple text parsing based on dataset type
            if dataset_type == DatasetType.QA:
                parts = text.split("\n", 1)
                if len(parts) >= 2:
                    return {"question": parts[0].strip(), "answer": parts[1].strip()}
            elif dataset_type == DatasetType.INSTRUCTION:
                parts = text.split("\n", 1)
                if len(parts) >= 2:
                    return {"instruction": parts[0].strip(), "response": parts[1].strip()}
            
            # Default fallback
            return {"generated": text.strip()} 