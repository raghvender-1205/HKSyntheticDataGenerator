import aiohttp
from typing import List, Dict

from app.services.base import BaseLLMService
from app.models import DatasetType


class GeminiLLMService(BaseLLMService):
    async def generate_synthetic_data(
        self,
        base_data: List[Dict],
        sample_size: int,
        dataset_type: DatasetType
    ) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.config.api_key
            }
            prompt = self._create_prompt(base_data, dataset_type, sample_size)  # Pass sample_size
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": 1000,
                    "candidateCount": sample_size
                }
            }
            async with session.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model_name}:generateContent",
                json=payload,
                headers=headers
            ) as response:
                result = await response.json()

                return self._format_response(result, dataset_type)

    def _create_prompt(self, base_data: List[Dict], dataset_type: DatasetType, sample_size: int) -> str:
        base_prompt = f"Generate {sample_size} synthetic {dataset_type.value} examples based on: {base_data}"
        if dataset_type == DatasetType.QA:
            return f"{base_prompt}\nReturn as Q: [question]\nA: [answer] pairs"
        elif dataset_type == DatasetType.INSTRUCTION:
            return f"{base_prompt}\nReturn as Instruction: [instr]\nResponse: [resp] pairs"
        elif dataset_type == DatasetType.CONVERSATION:
            return f"{base_prompt}\nReturn as multi-turn conversation blocks"

        return base_prompt

    def _format_response(self, result: Dict, dataset_type: DatasetType) -> List[Dict]:
        candidates = result.get("candidates", [])
        if dataset_type == DatasetType.QA:
            return [{"question": c["content"]["parts"][0]["text"].split("A:")[0][2:].strip(),
                    "answer": c["content"]["parts"][0]["text"].split("A:")[1].strip()}
                   for c in candidates]

        return [{"generated": c["content"]["parts"][0]["text"]} for c in candidates]