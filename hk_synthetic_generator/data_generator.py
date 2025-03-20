import os
import hashlib
import json

import pandas as pd
from dotenv import load_dotenv, find_dotenv
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.datamodel.base_models import InputFormat
from docling.chunking import HybridChunker

from langchain_community.document_loaders.base import BaseLoader
from langchain_ollama import ChatOllama
from langchain_core.documents import Document

from hk_synthetic_generator.vectorstore_indexer import VectorStoreIndexer
from hk_synthetic_generator.models import GenerationParams

load_dotenv(find_dotenv())


class HKDocumentLoader(BaseLoader):
    def load(self, folder_path: str) -> list[Document]:
        docs = []

        pipeline_options = PdfPipelineOptions(do_table_structure=True)
        pipeline_options.table_structure_options.do_cell_matching = False
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

        doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        chunker = HybridChunker(tokenizer="BAAI/bge-small-en-v1.5")

        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    # Convert and chunk the PDF
                    result = doc_converter.convert(file_path)
                    chunks = list(chunker.chunk(result.document))
                    base_filename = filename[:filename.rindex('.')].lower()
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            page_content=chunk.text,
                            metadata={
                                "filename": f"{base_filename}_chunk_{i}",
                                "hash": hashlib.md5(chunk.text.encode()).hexdigest(),
                                "type": "markdown",
                                "headings": chunk.meta.headings if chunk.meta.headings else [],
                                "page_numbers": list(set(
                                    item.prov[0].page_no
                                    for item in chunk.meta.doc_items
                                    if item.prov
                                ))
                            }
                        )
                        docs.append(doc)
                    print(f"Processed: {filename} into {len(chunks)} chunks")
        return docs


class HKSyntheticDataGenerator:
    def __init__(self):
        self.vector_store_indexer = VectorStoreIndexer()
        self.df = pd.DataFrame(columns=['instruction', 'input', 'response', 'context'])

    def generate_data(self, params: GenerationParams):
        self.llm = ChatOllama(
            base_url=os.getenv("OLLAMA_BASE_URL"),
            model="llama3.3:70b-instruct-q8_0",
        )
        loader = HKDocumentLoader()
        docs = loader.load(params.folder_path)
        for doc in docs:
            chunk = doc.page_content
            prompt = self.generate_question_prompt(chunk, params.questions_per_chunk)
            response = self.chat_with_llm(prompt)
            print(f"Questions: {response}")
            self.vector_store_indexer.index_data([doc])
            self.df = self.validate_json_questions_and_create_df(
                json_str=response,
                chunk=chunk,
                expected_count=params.questions_per_chunk,
                df=self.df
            )
        self.export_to_json()

    def generate_question_prompt(self, chunk: str, num_questions: int) -> str:
        return f"""
        Generate {num_questions} pairs of forward and backward QA pairs from this HR policy document chunk:
        {chunk}

        Requirements:
        1. For the Forward QA Pair:
           - Create a practical question that employees might ask.
           - Provide an answer that is either a verbatim excerpt or an accurate summary from the text.
        2. For the Backward QA Pair:
           - Reverse the roles by rephrasing the answer as a question that could lead someone back to the original question or context.
           - The original question should be included as supporting context to clarify the connection.
        3. Both pairs should use natural employee language and include various question types (what, how, who, etc.).

        Format:
        {{
            "qa_pairs": [
                {{
                    "forward": {{
                        "instruction": "forward question text",
                        "input": "relevant context excerpt",
                        "response": "forward answer text"
                    }},
                    "backward": {{
                        "instruction": "backward question text",
                        "input": "relevant context excerpt",
                        "response": "backward answer text"
                    }}
                }}
            ]
        }}
        """

    def chat_with_llm(self, user_message: str) -> str:
        combined_prompt = "You are a helpful assistant following the user's instructions.\n" + user_message
        response = self.llm.invoke(combined_prompt)
        print("RESPONSE: ", response)
        return response.content if hasattr(response, 'content') else str(response)

    def validate_json_questions_and_create_df(self, json_str: str, chunk: str, expected_count: int,
                                              df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Remove markdown code fences if present
            if '```' in json_str:
                start = json_str.find('{')
                end = json_str.rfind('}') + 1
                json_str = json_str[start:end] if start != -1 and end != -1 else json_str

            data = json.loads(json_str)
            # Ensure the expected count matches the number of QA pairs provided
            if not isinstance(data, dict) or len(data.get('qa_pairs', [])) != expected_count:
                return df

            # Add both forward and backward QA pairs to the DataFrame
            for qa in data['qa_pairs']:
                for pair_type in ['forward', 'backward']:
                    qa_pair = qa.get(pair_type)
                    if qa_pair:
                        row = {
                            "instruction": qa_pair.get('instruction', ''),
                            "input": qa_pair.get('input', ''),
                            "response": qa_pair.get('response', ''),
                            "context": chunk
                        }
                        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            return df
        except json.JSONDecodeError:
            return df

    def export_to_json(self, output_file="hr_qa_pairs.json"):
        """Exports QA pairs to JSON format suitable for fine-tuning"""
        if self.df.empty:
            print("No data to export")
            return

        qa_pairs = self.df[['instruction', 'input', 'response']].to_dict('records')
        with open(output_file, 'w') as f:
            json.dump(qa_pairs, f, indent=2)

        print(f"Exported {len(qa_pairs)} QA pairs to {output_file}")
