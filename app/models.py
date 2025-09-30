from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Document(Base):
    """Main documents table - stores uploaded files"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, jpg, etc.
    content = Column(Text)  # Full text content
    file_size = Column(Integer)
    is_public = Column(Boolean, default=False)  # Can others see this file?
    
    # Metadata as JSON (OCR confidence, page count, etc.)
    metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    """Text chunks for vector search - each document split into pieces"""
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    
    content = Column(Text, nullable=False)  # Chunk text
    chunk_index = Column(Integer, nullable=False)  # Which piece (0, 1, 2...)
    
    # For source attribution
    start_char = Column(Integer)  # Where chunk starts in original
    end_char = Column(Integer)    # Where chunk ends
    page_number = Column(Integer) # For PDFs
    
    # Vector embedding (stored as JSON array)
    embedding = Column(JSON)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")

class Conversation(Base):
    """Chat conversations with the AI"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    mode = Column(String, default="chat")  # chat, summarize, insights, planning
    
    # Sources used in response
    sources_used = Column(JSON, default=[])
    confidence_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class PublicShare(Base):
    """Track which files are shared publicly"""
    __tablename__ = "public_shares"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    share_token = Column(String, unique=True)  # Random token for public access
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration