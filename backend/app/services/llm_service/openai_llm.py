import aiohttp
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
        base_prompt = f"Generate {sample_size} synthetic {dataset_type.value} examples based on: {base_data}"
        if dataset_type == DatasetType.QA:
            return f"{base_prompt}\nFormat as question-answer pairs."
        elif dataset_type == DatasetType.INSTRUCTION:
            return f"{base_prompt}\nFormat as instruction-response pairs."
        elif dataset_type == DatasetType.CONVERSATION:
            return f"{base_prompt}\nFormat as multi-turn conversations."

        return base_prompt

    def _format_response(self, result: Dict, dataset_type: DatasetType) -> List[Dict]:
        choices = result.get("choices", [])
        if dataset_type == DatasetType.QA:
            return [{"question": c["text"].split("\n")[0], "answer": c["text"].split("\n")[1]}
                    for c in choices]

        return [{"generated": c["text"]} for c in choices]