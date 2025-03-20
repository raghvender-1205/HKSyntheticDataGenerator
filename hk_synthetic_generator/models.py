from dataclasses import dataclass


@dataclass
class GenerationParams:
    folder_path: str
    llm_choice: str = "ollama"
    questions_per_chunk: int = 50
    use_vectordb: bool = True