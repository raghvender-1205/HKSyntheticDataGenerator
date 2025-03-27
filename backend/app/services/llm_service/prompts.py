from typing import List, Dict
import json
from app.models import DatasetType

def get_base_prompt(base_data: List[Dict], dataset_type: DatasetType, sample_size: int) -> str:
    """Get the base prompt for synthetic data generation"""
    return f"""Generate {sample_size} unique and diverse synthetic {dataset_type.value} examples based on the following content. 
Each example should be distinct and cover different aspects of the content. Avoid repeating similar questions or topics.
Content: {json.dumps(base_data)}

Important guidelines:
1. Each example must be unique and different from others
2. Cover a wide range of topics and aspects from the content
3. Vary the complexity and depth of questions
4. Ensure answers are accurate and based on the provided content
5. Format the output as a JSON array of objects
6. DO NOT include any markdown formatting or code block markers
7. Return ONLY the JSON array, no additional text

"""

def get_dataset_specific_prompt(base_prompt: str, dataset_type: DatasetType) -> str:
    """Get the dataset-specific formatting instructions"""
    if dataset_type == DatasetType.QA:
        return f"{base_prompt}Format as a JSON array of question-answer pairs with 'question' and 'answer' fields."
    elif dataset_type == DatasetType.INSTRUCTION:
        return f"{base_prompt}Format as a JSON array of instruction-response pairs with 'instruction' and 'response' fields."
    elif dataset_type == DatasetType.CONVERSATION:
        return f"{base_prompt}Format as a JSON array of conversations with 'messages' field containing an array of message objects with 'role' and 'content'."
    elif dataset_type == DatasetType.CLASSIFICATION:
        return f"{base_prompt}Format as a JSON array of classification examples with 'text' and 'label' fields."
    
    return f"{base_prompt}Provide output as a JSON array of objects." 