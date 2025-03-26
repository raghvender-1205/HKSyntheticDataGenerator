import aiohttp
import json
from typing import List, Dict

from app.models import DatasetType
from app.services.base import BaseLLMService


class OpenAILLMService(BaseLLMService):
    async def generate_synthetic_data(
            self,
            base_data: List[Dict],
            sample_size: int,
            dataset_type: DatasetType
    ) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.config.api_key}"}
            prompt = self._create_prompt(base_data, dataset_type, sample_size)  # Pass sample_size
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "max_tokens": 1000,
                "n": sample_size
            }
            async with session.post(
                    "https://api.openai.com/v1/completions",
                    json=payload,
                    headers=headers
            ) as response:
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
        if dataset_type == DatasetType.QA:
            return [{"question": c["text"].split("\n")[0], "answer": c["text"].split("\n")[1]}
                    for c in choices]

        return [{"generated": c["text"]} for c in choices]