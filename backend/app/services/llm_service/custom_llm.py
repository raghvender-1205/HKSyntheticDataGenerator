import aiohttp
import json
from typing import List, Dict

from app.models import DatasetType, LLMConfig
from app.services.base import BaseLLMService


class CustomLLMService(BaseLLMService):
    def __init__(self, config: Dict):
        super().__init__(config)
        # Initialize parameters to empty dict if None
        if not isinstance(config, dict) or 'parameters' not in config:
            self.parameters = {}
        else:
            self.parameters = config['parameters']
        # Extract API base URL from parameters or use default
        self.api_base_url = self.parameters.get("api_base_url", "http://localhost:8000/v1")
        self.api_key = config.get('api_key')
        self.model_name = config.get('model_name')
        
    async def generate_synthetic_data(
            self,
            base_data: List[Dict],
            sample_size: int,
            dataset_type: DatasetType
    ) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            prompt = self._create_prompt(base_data, dataset_type, sample_size)
            
            # Get additional parameters from config
            temperature = self.parameters.get("temperature", 0.7)
            max_tokens = self.parameters.get("max_tokens", 1000)
            
            # Construct the payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "n": sample_size
            }
            
            # Add any additional parameters from config
            for key, value in self.parameters.items():
                if key not in ["api_base_url", "temperature", "max_tokens"]:
                    payload[key] = value
            
            # Make request to the custom vLLM endpoint
            completions_url = f"{self.api_base_url}/completions"
            async with session.post(
                    completions_url,
                    json=payload,
                    headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"vLLM API error: {response.status}, {error_text}")
                
                result = await response.json()
                return self._format_response(result, dataset_type)

    def _create_prompt(self, base_data: List[Dict], dataset_type: DatasetType, sample_size: int) -> str:
        base_prompt = f"""Generate {sample_size} unique and diverse synthetic {dataset_type.value} examples based on the following content. 
Each example should be distinct and cover different aspects of the content. Avoid repeating similar questions or topics.
Content: {json.dumps(base_data)}

Important guidelines:
1. Each example must be unique and different from others
2. Cover a wide range of topics and aspects from the content
3. Vary the complexity and depth of questions
4. Ensure answers are accurate and based on the provided content
5. Format the output as a JSON array of objects

"""
        
        if dataset_type == DatasetType.QA:
            return f"{base_prompt}Format as a JSON array of question-answer pairs with 'question' and 'answer' fields."
        elif dataset_type == DatasetType.INSTRUCTION:
            return f"{base_prompt}Format as a JSON array of instruction-response pairs with 'instruction' and 'response' fields."
        elif dataset_type == DatasetType.CONVERSATION:
            return f"{base_prompt}Format as a JSON array of conversations with 'messages' field containing an array of message objects with 'role' and 'content'."
        elif dataset_type == DatasetType.CLASSIFICATION:
            return f"{base_prompt}Format as a JSON array of classification examples with 'text' and 'label' fields."
        
        return f"{base_prompt}Provide output as a JSON array of objects."

    def _format_response(self, result: Dict, dataset_type: DatasetType) -> List[Dict]:
        choices = result.get("choices", [])
        
        if not choices:
            return []
            
        if dataset_type == DatasetType.QA:
            formatted_data = []
            for c in choices:
                text = c.get("text", "")
                parts = text.split("\n", 1)
                if len(parts) >= 2:
                    formatted_data.append({"question": parts[0].strip(), "answer": parts[1].strip()})
                else:
                    formatted_data.append({"question": text.strip(), "answer": ""})
            return formatted_data
        elif dataset_type == DatasetType.INSTRUCTION:
            formatted_data = []
            for c in choices:
                text = c.get("text", "")
                parts = text.split("\n", 1)
                if len(parts) >= 2:
                    formatted_data.append({"instruction": parts[0].strip(), "response": parts[1].strip()})
                else:
                    formatted_data.append({"instruction": text.strip(), "response": ""})
            return formatted_data
        elif dataset_type == DatasetType.CLASSIFICATION:
            formatted_data = []
            for c in choices:
                text = c.get("text", "")
                parts = text.split("\n", 1)
                if len(parts) >= 2:
                    formatted_data.append({"text": parts[0].strip(), "label": parts[1].strip()})
                else:
                    formatted_data.append({"text": text.strip(), "label": ""})
            return formatted_data

        # Default format for other dataset types
        return [{"generated": c.get("text", "")} for c in choices] 