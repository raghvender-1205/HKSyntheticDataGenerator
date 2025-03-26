import google.generativeai as genai
from typing import List, Dict, Any
import json

from app.services.base import BaseLLMService
from app.models import DatasetType


class GeminiLLMService(BaseLLMService):
    def __init__(self, config: Dict):
        super().__init__(config)
        # Handle config as dictionary
        if isinstance(config, dict):
            self.api_key = config.get('api_key', '')
            self.model_name = config.get('model_name', 'gemini-pro')
            self.parameters = config.get('parameters', {}) or {}
        else:
            # Fallback for object-style config
            self.api_key = getattr(config, 'api_key', '')
            self.model_name = getattr(config, 'model_name', 'gemini-pro')
            self.parameters = getattr(config, 'parameters', {}) or {}
        
        # Configure the genai client
        genai.configure(api_key=self.api_key)

    async def generate_synthetic_data(
        self,
        base_data: List[Dict],
        sample_size: int,
        dataset_type: DatasetType
    ) -> List[Dict]:
        try:
            # Create model instance
            model = genai.GenerativeModel(self.model_name)
            
            # Prepare prompt
            prompt = self._create_prompt(base_data, dataset_type, sample_size)
            
            # Extract generation parameters with defaults
            temperature = float(self.parameters.get("temperature", 0.7))
            max_tokens = int(self.parameters.get("max_tokens", 1000))
            
            # Configure generation parameters
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            # Add additional parameters if provided
            if "top_p" in self.parameters:
                generation_config["top_p"] = float(self.parameters.get("top_p"))
            if "top_k" in self.parameters:
                generation_config["top_k"] = int(self.parameters.get("top_k"))
                
            # Generate responses
            all_results = []
            for _ in range(sample_size):
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                # Process the response
                if hasattr(response, 'text'):
                    result_text = response.text
                    try:
                        # First try parsing as JSON
                        result_data = json.loads(result_text)
                        all_results.append(result_data)
                    except json.JSONDecodeError:
                        # If not JSON, process as text
                        result_dict = self._parse_text_response(result_text, dataset_type)
                        all_results.append(result_dict)
            
            return all_results
        except Exception as e:
            print(f"Error generating with Gemini: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")

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
        
        # Add specific formatting instructions
        if dataset_type == DatasetType.QA:
            return f"{base_prompt}Return as a JSON array of objects in this format: [{{\"question\": \"...\", \"answer\": \"...\"}}]"
        elif dataset_type == DatasetType.INSTRUCTION:
            return f"{base_prompt}Return as a JSON array of objects in this format: [{{\"instruction\": \"...\", \"response\": \"...\"}}]"
        elif dataset_type == DatasetType.CONVERSATION:
            return f"{base_prompt}Return as a JSON array of objects with conversation turns in this format: [{{\"conversation\": [{{\"role\": \"user\", \"content\": \"...\"}}]}}]"
        
        return base_prompt
    
    def _parse_text_response(self, text: str, dataset_type: DatasetType) -> Dict:
        """Parse text response when JSON parsing fails"""
        if dataset_type == DatasetType.QA:
            # Try to extract question-answer pairs
            if "Q:" in text and "A:" in text:
                parts = text.split("Q:", 1)[1].split("A:")
                if len(parts) >= 2:
                    return {
                        "question": parts[0].strip(),
                        "answer": parts[1].strip()
                    }
        elif dataset_type == DatasetType.INSTRUCTION:
            # Try to extract instruction-response pairs
            if "Instruction:" in text and "Response:" in text:
                parts = text.split("Instruction:", 1)[1].split("Response:")
                if len(parts) >= 2:
                    return {
                        "instruction": parts[0].strip(),
                        "response": parts[1].strip()
                    }
        
        # Default fallback
        return {"content": text.strip()}
    
    def _format_response(self, result: Dict, dataset_type: DatasetType) -> List[Dict]:
        """
        Format the response based on the dataset type.
        This is a compatibility method to maintain the same interface.
        """
        # This method would be used when calling directly through the API
        if not result or not isinstance(result, dict):
            return []
        
        formatted_responses = []
        
        # Extract content from the Google API response format
        if "candidates" in result:
            for candidate in result["candidates"]:
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "text" in part:
                            try:
                                parsed = json.loads(part["text"])
                                formatted_responses.append(parsed)
                            except json.JSONDecodeError:
                                parsed = self._parse_text_response(part["text"], dataset_type)
                                formatted_responses.append(parsed)
        
        return formatted_responses