# utils.py
import PyPDF2
from docx import Document
import json

def extract_text(file_path):
    """Extract text from various file formats"""
    if file_path.endswith(".pdf"):
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_path.endswith(".json"):
        # Instagram chat JSON or other JSON formats
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            messages = []
            for msg in data.get("messages", []):
                text = msg.get("text")
                if isinstance(text, str):
                    messages.append(text)
                elif isinstance(text, list):
                    messages.append(" ".join([t.get("text","") for t in text if isinstance(t, dict)]))
            return "\n".join(messages)
    else:
        return ""

def chunk_text(text, chunk_size=500):
    """Split text into smaller chunks for vector storage"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks