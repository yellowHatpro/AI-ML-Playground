from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
class VectorStore:
    def __init__(self, source_file: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.loader = TextLoader(source_file)
        self.documents = self.loader.load()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings = OpenAIEmbeddings()
        self.db = FAISS.from_documents(self.split_documents(), self.embeddings)

    def split_documents(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        return text_splitter.split_documents(self.documents)
    
    def get_embeddings(self):
        return self.embeddings
    
    def get_db(self):
        return self.db
    
    def add_documents(self, documents: list):
        self.db.add_documents(documents)
        return self.db