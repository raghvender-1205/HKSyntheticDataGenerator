import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from core.dataset_generator import DatasetGenerator, DatasetGeneratorConfig, Dataset, DatasetItem
from core.datasource import Document
from core.llm import LLMProvider

class QAGeneratorConfig(DatasetGeneratorConfig):
    """
    Configuration for the QA dataset generator.
    """
    generator_type: str = "qa"
    questions_per_document: int = 5
    include_document_content: bool = True
    format: str = "qa"  # qa, instruction
    question_template: Optional[str] = None
    answer_template: Optional[str] = None

class QAGenerator(DatasetGenerator):
    """
    A dataset generator that creates question-answer pairs from documents.
    """
    plugin_id = "qa_generator"
    
    def __init__(self, config: QAGeneratorConfig):
        """
        Initialize the QA dataset generator.
        
        Args:
            config: Configuration for the QA dataset generator
        """
        self.config = config
        self.questions_per_document = config.questions_per_document
        self.include_document_content = config.include_document_content
        self.format = config.format
        self.question_template = config.question_template
        self.answer_template = config.answer_template
    
    async def generate(
        self, 
        documents: List[Document], 
        llm_provider: LLMProvider, 
        **kwargs
    ) -> Dataset:
        """
        Generate QA pairs from documents using the specified LLM provider.
        
        Args:
            documents: A list of documents to generate QA pairs from
            llm_provider: The LLM provider to use
            **kwargs: Additional parameters for the dataset generation
            
        Returns:
            A Dataset object
        """
        questions_per_document = kwargs.get("questions_per_document", self.questions_per_document)
        
        # Create dataset
        dataset = Dataset(
            name=f"QA Dataset - {len(documents)} documents",
            description=f"Question-answer pairs generated from {len(documents)} documents",
            items=[],
            metadata={
                "generator": self.plugin_id,
                "document_count": len(documents),
                "questions_per_document": questions_per_document,
                "format": self.format
            }
        )
        
        # Generate QA pairs for each document
        for i, document in enumerate(documents):
            # Create a prompt for generating QA pairs
            if self.format.lower() == "qa":
                prompt = f"""I have the following text:

{document.content}

Based on the content above, generate {questions_per_document} question-answer pairs. 
Each question should be answerable from the text. Keep the answers concise but informative. 
Each pair should be in the following JSON format:
{{
  "question": "Write the question here",
  "answer": "Write the answer here"
}}

Return all {questions_per_document} pairs together in a JSON array."""
            else:  # instruction format
                prompt = f"""I have the following text:

{document.content}

Based on the content above, generate {questions_per_document} instruction-response pairs that would be suitable for fine-tuning an LLM.
Each instruction should be based on the text. The response should be what a good assistant would say in response to the instruction.
Each pair should be in the following JSON format:
{{
  "instruction": "Write the instruction here",
  "response": "Write the response here"
}}

Return all {questions_per_document} pairs together in a JSON array."""
            
            # Generate QA pairs using the LLM
            llm_response = await llm_provider.generate(prompt)
            
            # Parse the response
            try:
                pairs = parse_llm_json_response(llm_response.text)
                
                # Check if the response is valid
                if not isinstance(pairs, list):
                    continue
                
                for pair in pairs:
                    if self.format.lower() == "qa":
                        if "question" not in pair or "answer" not in pair:
                            continue
                        
                        # Add custom templates if specified
                        question = pair["question"]
                        answer = pair["answer"]
                        
                        if self.question_template:
                            question = self.question_template.replace("{{question}}", question)
                        
                        if self.answer_template:
                            answer = self.answer_template.replace("{{answer}}", answer)
                        
                        item_data = {
                            "question": question,
                            "answer": answer
                        }
                    else:  # instruction format
                        if "instruction" not in pair or "response" not in pair:
                            continue
                        
                        item_data = {
                            "instruction": pair["instruction"],
                            "response": pair["response"]
                        }
                    
                    # Add document content if specified
                    if self.include_document_content:
                        item_data["context"] = document.content
                    
                    # Add to dataset
                    dataset.items.append(DatasetItem(
                        data=item_data,
                        metadata={
                            "document_index": i,
                            "source": document.metadata.get("source", "unknown"),
                            "format": self.format
                        }
                    ))
            except Exception as e:
                print(f"Error parsing LLM response: {e}")
                print(f"Response: {llm_response.text}")
                continue
        
        return dataset
    
    async def get_info(self) -> Dict[str, Any]:
        """
        Get information about the dataset generator.
        
        Returns:
            A dictionary with information about the dataset generator
        """
        return {
            "id": self.plugin_id,
            "name": self.config.name,
            "description": self.config.description,
            "generator_type": "qa",
            "format": self.format,
            "questions_per_document": self.questions_per_document,
            "include_document_content": self.include_document_content
        }
    
    @staticmethod
    def get_config_schema() -> Dict[str, Any]:
        """
        Get the JSON schema for the dataset generator configuration.
        
        Returns:
            A dictionary representing the JSON schema
        """
        return {
            "title": "QA Dataset Generator Configuration",
            "type": "object",
            "properties": {
                "generator_id": {
                    "type": "string",
                    "title": "Generator ID",
                    "description": "Unique identifier for the dataset generator",
                },
                "name": {
                    "type": "string",
                    "title": "Name",
                    "description": "Display name for the dataset generator",
                },
                "description": {
                    "type": "string",
                    "title": "Description",
                    "description": "Description of the dataset generator",
                },
                "generator_type": {
                    "type": "string",
                    "title": "Generator Type",
                    "description": "Type of dataset generator",
                    "default": "qa",
                    "enum": ["qa"],
                },
                "questions_per_document": {
                    "type": "integer",
                    "title": "Questions Per Document",
                    "description": "Number of questions to generate per document",
                    "default": 5,
                    "minimum": 1,
                },
                "include_document_content": {
                    "type": "boolean",
                    "title": "Include Document Content",
                    "description": "Whether to include the document content in the dataset",
                    "default": True,
                },
                "format": {
                    "type": "string",
                    "title": "Format",
                    "description": "Format of the generated pairs",
                    "default": "qa",
                    "enum": ["qa", "instruction"],
                },
                "question_template": {
                    "type": "string",
                    "title": "Question Template",
                    "description": "Template for questions (use {{question}} as placeholder)",
                },
                "answer_template": {
                    "type": "string",
                    "title": "Answer Template",
                    "description": "Template for answers (use {{answer}} as placeholder)",
                },
            },
            "required": ["generator_id", "name"],
        }

def parse_llm_json_response(response: str) -> Any:
    """
    Parse a JSON response from an LLM.
    
    Args:
        response: The response text from the LLM
        
    Returns:
        The parsed JSON object
    """
    # Find JSON array in the response
    start_idx = response.find("[")
    end_idx = response.rfind("]") + 1
    
    if start_idx >= 0 and end_idx > start_idx:
        # Extract JSON array
        json_str = response[start_idx:end_idx]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object instead
    start_idx = response.find("{")
    end_idx = response.rfind("}") + 1
    
    if start_idx >= 0 and end_idx > start_idx:
        # Extract JSON object
        json_str = response[start_idx:end_idx]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try with code blocks (markdown format)
    if "```json" in response:
        parts = response.split("```json")
        if len(parts) > 1:
            json_part = parts[1].split("```")[0].strip()
            try:
                return json.loads(json_part)
            except json.JSONDecodeError:
                pass
    
    if "```" in response:
        parts = response.split("```")
        if len(parts) > 1:
            json_part = parts[1].strip()
            try:
                return json.loads(json_part)
            except json.JSONDecodeError:
                pass
    
    # Try to parse the whole response
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Return empty list if all parsing attempts fail
        return [] 