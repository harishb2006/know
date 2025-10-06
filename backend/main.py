# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from backend.services.utils import extract_text, chunk_text
from backend.services.database import documents_collection, conversations_collection, users_collection
from backend.services.vectorstore import collection, get_embedding
from backend.models.auth import (
    authenticate_user, create_access_token, get_current_user, 
    get_password_hash, UserCreate, UserLogin, Token, User,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
import google.generativeai as genai
import uuid

load_dotenv()

app = FastAPI(title="Knowledge Assistant with Authentication", version="2.0.0")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class Question(BaseModel):
    question: str

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = users_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = users_collection.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user_doc = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    users_collection.insert_one(user_doc)
    
    return {"message": "User registered successfully"}

@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return access token"""
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=User)
async def read_users_me(current_user = Depends(get_current_user)):
    """Get current user information"""
    return User(
        username=current_user["username"],
        email=current_user["email"],
        created_at=current_user["created_at"]
    )

# ==================== DOCUMENT MANAGEMENT ENDPOINTS ====================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...), 
    current_user = Depends(get_current_user)
):
    """Upload and process a document"""
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text content
    text = extract_text(file_path)
    
    # Store document metadata in MongoDB
    doc_metadata = {
        "filename": file.filename,
        "text": text,
        "type": "document",
        "user_id": current_user["username"],
        "upload_date": datetime.utcnow()
    }
    documents_collection.insert_one(doc_metadata)

    # Create chunks and store in vector database
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        if embedding:
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "source": file.filename, 
                    "chunk": i, 
                    "type": "document",
                    "user_id": current_user["username"]
                }],
                ids=[str(uuid.uuid4())]
            )

    return {"message": f"{file.filename} uploaded and stored successfully."}

@app.post("/upload-chat")
async def upload_chat(
    file: UploadFile = File(...), 
    current_user = Depends(get_current_user)
):
    """Upload and process chat/conversation files"""
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text content
    text = extract_text(file_path)
    
    # Store chat metadata in MongoDB
    chat_metadata = {
        "filename": file.filename,
        "text": text,
        "type": "chat",
        "user_id": current_user["username"],
        "upload_date": datetime.utcnow()
    }
    documents_collection.insert_one(chat_metadata)

    # Create chunks and store in vector database
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        if embedding:
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "source": file.filename, 
                    "chunk": i, 
                    "type": "chat",
                    "user_id": current_user["username"]
                }],
                ids=[str(uuid.uuid4())]
            )

    return {"message": f"{file.filename} chat uploaded and stored successfully."}

# ==================== QUESTION ANSWERING ENDPOINT ====================

@app.post("/ask")
async def ask_question(
    q: Question, 
    current_user = Depends(get_current_user)
):
    """Ask a question and get AI-powered answer based on user's documents"""
    # Get embedding for the question
    query_embedding = get_embedding(q.question)
    if not query_embedding:
        raise HTTPException(status_code=500, detail="Failed to generate embedding for query")
    
    # Retrieve top 3 relevant chunks using vector similarity
    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=3,
        where={"user_id": current_user["username"]}  # Filter by user
    )
    relevant_texts = " ".join([doc for doc in results['documents'][0]]) if results['documents'] else ""

    # Retrieve past conversation history for context
    past_conv = conversations_collection.find_one({
        "user_id": current_user["username"]
    })
    memory_text = "\n".join(past_conv.get("history", [])) if past_conv else ""

    # Create prompt for AI
    prompt = f"""
    You are a helpful assistant. Reference the uploaded documents and chats.
    Past conversation: {memory_text}
    Relevant content: {relevant_texts}
    Question: {q.question}
    Provide a concise answer with key takeaways.
    """

    # Get response from AI (Gemini)
    response = gemini_model.generate_content(prompt)
    answer = response.text

    # Save conversation to memory
    conversation_entry = f"Q: {q.question}\nA: {answer}"
    if past_conv:
        conversations_collection.update_one(
            {"user_id": current_user["username"]},
            {"$push": {"history": conversation_entry}}
        )
    else:
        conversations_collection.insert_one({
            "user_id": current_user["username"], 
            "history": [conversation_entry],
            "created_at": datetime.utcnow()
        })

    return {"answer": answer}

# ==================== DOCUMENT LISTING ENDPOINT ====================

@app.get("/documents")
async def list_documents(current_user = Depends(get_current_user)):
    """List all documents for the current user"""
    docs_cursor = documents_collection.find(
        {"user_id": current_user["username"]}, 
        {"filename": 1, "type": 1, "upload_date": 1, "text": 1}
    )
    docs = []
    for doc in docs_cursor:
        # Calculate file size from text length (approximate)
        text_content = doc.get("text", "")
        file_size = len(text_content.encode('utf-8'))
        
        docs.append({
            "id": str(doc["_id"]),
            "filename": doc["filename"],
            "type": doc["type"],
            "upload_date": doc["upload_date"].isoformat(),
            "file_size": file_size,
            "content_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content
        })
    
    return docs

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: str, 
    current_user = Depends(get_current_user)
):
    """Delete a document for the current user"""
    from bson import ObjectId
    
    # Verify document belongs to user and delete
    result = documents_collection.delete_one({
        "_id": ObjectId(document_id),
        "user_id": current_user["username"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or not authorized"
        )
    
    # Also remove vector embeddings for this document
    # Note: This is a basic implementation - in production you'd want more sophisticated cleanup
    try:
        collection.delete(
            where={"source": {"$ne": None}, "user_id": current_user["username"]}
        )
    except Exception as e:
        # Log error but don't fail the deletion
        print(f"Warning: Could not clean up vector embeddings: {e}")
    
    return {"message": "Document deleted successfully"}

# ==================== HEALTH CHECK ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Knowledge Assistant API with Authentication", 
        "version": "2.0.0",
        "status": "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)