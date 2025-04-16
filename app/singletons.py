from chromadb import Client, Collection
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.constants import COLLECTION_NAME, PERSISTENT_DIRECTORY
from app.utils import console


class ChromaDB:
    def __init__(self):
        self.__settings = Settings(PERSISTENT_DIRECTORY, is_persistent=True)
        self.__client = Client(self.__settings)
        self.__collection = self.__client.get_or_create_collection(COLLECTION_NAME)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    @property
    def collection(self) -> Collection:
        return self.__collection

    def get_embedding(self, text: str) -> list:
        try:
            embedding = self.model.encode(text).tolist()
            return embedding
        except Exception as e:
            console.print(f"[red]Error obtaining embedding: {e}[/red]")
            return None


_chromadb_instance = None


def get_chromadb():
    global _chromadb_instance
    if _chromadb_instance is None:
        _chromadb_instance = ChromaDB()
    return _chromadb_instance
