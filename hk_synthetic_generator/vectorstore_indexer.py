import os
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class VectorStoreIndexer:
    def __init__(self):
        self.client = QdrantClient(url=os.getenv("QDRANT_URL"))
        self.COLLECTION_NAME = os.environ.get("COLLECTION_NAME")
        self.model = OllamaEmbeddings(
            base_url=os.getenv("OLLAMA_BASE_URL"),
            model="bge-m3:567m-fp16",
        )
        if not self.client.collection_exists(collection_name=self.COLLECTION_NAME):
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
            )

    def index_data(self, docs):
        vs = QdrantVectorStore(
            client=self.client,
            collection_name=self.COLLECTION_NAME,
            embedding=self.model
        )
        vs.add_documents(docs)
        print("data indexed")
