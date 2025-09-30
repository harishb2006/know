from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from app.database import get_db
from app.config import settings
from services.document_service import DocumentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])
document_service = DocumentService()

class DocumentResponse(BaseModel):
    """Document response model"""
    success: bool
    document_id: Optional[str] = None
    filename: Optional[str] = None
    chunks_created: Optional[int] = None
    text_preview: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SearchResponse(BaseModel):
    """Search response model"""
    query: str
    results: List[Dict[str, Any]]
    total_results: int

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    is_public: bool = Form(False, description="Make document publicly accessible"),
    db: Session = Depends(get_db)
):
    """
    Upload and process document with text extraction and embedding generation
    
    Supports:
    - PDF files (text extraction)
    - DOCX files (text extraction) 
    - Images (OCR text extraction): JPG, JPEG, PNG, TIFF, BMP
    - Plain text files
    
    Features:
    - Automatic text extraction
    - Document chunking for semantic search
    - Vector embedding generation
    - OCR for image-based documents
    - Public sharing option
    """
    try:
        # Validate file size
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {settings.max_file_size / (1024*1024):.1f}MB"
            )
        
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        file_extension = file.filename.lower().split('.')[-1]
        supported_types = ['pdf', 'docx', 'doc', 'txt', 'jpg', 'jpeg', 'png', 'tiff', 'bmp']
        
        if file_extension not in supported_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Supported: {', '.join(supported_types)}"
            )
        
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        logger.info(f"Processing upload: {file.filename} ({len(content)} bytes)")
        
        # Process document
        result = document_service.upload_document(content, file.filename, is_public)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return DocumentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during upload")

@router.get("/search", response_model=SearchResponse)
async def search_documents(
    query: str, 
    k: int = 5,
    include_private: bool = True
):
    """
    Search documents using semantic similarity
    
    Uses vector embeddings to find the most relevant document chunks
    for your query. Results include similarity scores and source attribution.
    
    Args:
        query: Search query text
        k: Number of results to return (1-20)
        include_private: Include private documents in search results
    """
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if k < 1 or k > 20:
            raise HTTPException(status_code=400, detail="k must be between 1 and 20")
        
        logger.info(f"Searching documents: '{query[:100]}...' (k={k})")
        
        # Search documents
        results = document_service.search_documents(query, k)
        
        # Filter private documents if requested
        if not include_private:
            results = [r for r in results if r.get('is_public', False)]
        
        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.get("/public")
async def list_public_documents(skip: int = 0, limit: int = 50):
    """
    List publicly accessible documents
    
    Returns documents that have been marked as public for browsing
    and sharing.
    """
    try:
        if limit > 100:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 100")
        
        documents = document_service.get_public_documents(skip, limit)
        
        return {
            "documents": documents,
            "total": len(documents),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to list public documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list public documents")

@router.get("/{document_id}")
async def get_document(document_id: str):
    """
    Get document details by ID
    
    Returns full document information including content, metadata,
    and processing details.
    """
    try:
        document = document_service.get_document_by_id(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve document")

@router.get("/")
async def list_all_documents(skip: int = 0, limit: int = 50):
    """
    List all documents (public and private)
    
    Returns all documents in the system with basic information.
    """
    try:
        if limit > 100:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 100")
        
        # This could be extended to include user filtering in a full implementation
        documents = document_service.get_public_documents(skip, limit * 2)  # Get more to account for private docs
        
        return {
            "documents": documents,
            "total": len(documents),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")

@router.get("/stats/summary")
async def get_document_stats():
    """
    Get document statistics
    
    Returns summary statistics about uploaded documents.
    """
    try:
        # This is a basic implementation - could be enhanced with actual database queries
        from app.database import get_db_sync
        from app.models import Document
        
        db = get_db_sync()
        try:
            total_docs = db.query(Document).count()
            public_docs = db.query(Document).filter(Document.is_public == True).count()
            
            # File type distribution
            file_types = {}
            docs = db.query(Document).all()
            for doc in docs:
                file_type = doc.file_type
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            return {
                "total_documents": total_docs,
                "public_documents": public_docs,
                "private_documents": total_docs - public_docs,
                "file_type_distribution": file_types
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Failed to get document stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document statistics")