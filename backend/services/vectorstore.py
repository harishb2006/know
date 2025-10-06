# vectorstore.py
import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini for embeddings
def get_embedding(text):
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result["embedding"]
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Create or get collection for documents
collection = client.get_or_create_collection(
    name="documents"
)