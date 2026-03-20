import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity

#----------------------------------------------------------
def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_text(text)

    # Remove duplicates AFTER splitting
    chunks = list(dict.fromkeys(chunks))  # preserves order

    return chunks

#----------------------------------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text):
    vec = model.encode(text)
    return vec / np.linalg.norm(vec)

#----------------------------------------------------------

class VectorStore:

    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings, texts):
        self.index.add(np.array(embeddings).astype("float32"))
        self.texts.extend(texts)

    def search(self, query_embedding, k=3):
        D, I = self.index.search(
            np.array([query_embedding]).astype("float32"), k
        )
        return [
    self.texts[i] for i in I[0]
    if i != -1 and i < len(self.texts)
]
vector_store = VectorStore()   
#----------------------------------------------------------
def retrieve(query, top_k=2):
    query_embedding = embed(query)
    return vector_store.search(query_embedding, k=top_k)