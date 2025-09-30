from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import secrets
import os
import logging
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Document, PublicShare
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/public", tags=["public"])

class PublicShareRequest(BaseModel):
    """Request to create a public share"""
    document_id: str
    expires_in_days: Optional[int] = None  # None = no expiration

class PublicShareResponse(BaseModel):
    """Public share response"""
    share_token: str
    public_url: str
    expires_at: Optional[str]
    document_name: str

@router.post("/share", response_model=PublicShareResponse)
async def create_public_share(
    request: PublicShareRequest,
    db: Session = Depends(get_db)
):
    """
    Create a public share link for a document
    
    Generates a secure, shareable link that allows public access to a document
    without requiring authentication.
    """
    try:
        # Check if document exists and is owned by user
        document = db.query(Document).filter(Document.id == request.document_id).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate secure token
        share_token = secrets.token_urlsafe(32)
        
        # Calculate expiration if specified
        expires_at = None
        if request.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
        
        # Check if share already exists
        existing_share = db.query(PublicShare).filter(
            PublicShare.document_id == request.document_id
        ).first()
        
        if existing_share:
            # Update existing share
            existing_share.share_token = share_token
            existing_share.expires_at = expires_at
            public_share = existing_share
        else:
            # Create new share
            public_share = PublicShare(
                document_id=request.document_id,
                share_token=share_token,
                expires_at=expires_at
            )
            db.add(public_share)
        
        # Mark document as public
        document.is_public = True
        
        db.commit()
        
        # Generate public URL
        public_url = f"{settings.frontend_url}/public/{share_token}"
        
        return PublicShareResponse(
            share_token=share_token,
            public_url=public_url,
            expires_at=expires_at.isoformat() if expires_at else None,
            document_name=document.filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create public share: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create public share")

@router.get("/document/{share_token}")
async def get_public_document(share_token: str, db: Session = Depends(get_db)):
    """
    Get a publicly shared document by token
    
    Retrieves document information and content using a public share token.
    No authentication required.
    """
    try:
        # Find the public share
        public_share = db.query(PublicShare).filter(
            PublicShare.share_token == share_token
        ).first()
        
        if not public_share:
            raise HTTPException(status_code=404, detail="Public share not found")
        
        # Check if share has expired
        if public_share.expires_at and public_share.expires_at < datetime.utcnow():
            raise HTTPException(status_code=410, detail="Public share has expired")
        
        # Get the document
        document = db.query(Document).filter(
            Document.id == public_share.document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "content": document.content,
            "file_size": document.file_size,
            "metadata": document.metadata,
            "created_at": document.created_at.isoformat(),
            "share_info": {
                "share_token": share_token,
                "expires_at": public_share.expires_at.isoformat() if public_share.expires_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get public document: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve public document")

@router.get("/download/{share_token}")
async def download_public_document(share_token: str, db: Session = Depends(get_db)):
    """
    Download a publicly shared document file
    
    Downloads the original file using a public share token.
    """
    try:
        # Find the public share
        public_share = db.query(PublicShare).filter(
            PublicShare.share_token == share_token
        ).first()
        
        if not public_share:
            raise HTTPException(status_code=404, detail="Public share not found")
        
        # Check if share has expired
        if public_share.expires_at and public_share.expires_at < datetime.utcnow():
            raise HTTPException(status_code=410, detail="Public share has expired")
        
        # Get the document
        document = db.query(Document).filter(
            Document.id == public_share.document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get file path from metadata
        file_path = document.metadata.get('file_path')
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on server")
        
        return FileResponse(
            path=file_path,
            filename=document.filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download public document: {e}")
        raise HTTPException(status_code=500, detail="Failed to download document")

@router.get("/list")
async def list_public_documents(
    skip: int = 0, 
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List all publicly available documents
    
    Returns a list of documents that have been made public for browsing.
    """
    try:
        if limit > 100:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 100")
        
        # Get public documents
        documents = db.query(Document).filter(
            Document.is_public == True
        ).offset(skip).limit(limit).all()
        
        # Get total count
        total = db.query(Document).filter(Document.is_public == True).count()
        
        document_list = []
        for doc in documents:
            # Get share info if available
            share_info = db.query(PublicShare).filter(
                PublicShare.document_id == doc.id
            ).first()
            
            document_list.append({
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "created_at": doc.created_at.isoformat(),
                "metadata": {
                    "total_pages": doc.metadata.get("total_pages", 1),
                    "extraction_method": doc.metadata.get("extraction_method", "unknown")
                },
                "share_token": share_info.share_token if share_info else None
            })
        
        return {
            "documents": document_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to list public documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list public documents")

@router.delete("/share/{share_token}")
async def revoke_public_share(share_token: str, db: Session = Depends(get_db)):
    """
    Revoke a public share
    
    Removes public access to a document by deleting the share token.
    """
    try:
        # Find the public share
        public_share = db.query(PublicShare).filter(
            PublicShare.share_token == share_token
        ).first()
        
        if not public_share:
            raise HTTPException(status_code=404, detail="Public share not found")
        
        document_id = public_share.document_id
        
        # Delete the share
        db.delete(public_share)
        
        # Check if there are other shares for this document
        other_shares = db.query(PublicShare).filter(
            PublicShare.document_id == document_id
        ).count()
        
        # If no other shares, mark document as not public
        if other_shares == 0:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.is_public = False
        
        db.commit()
        
        return {
            "message": "Public share revoked successfully",
            "share_token": share_token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke public share: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to revoke public share")

@router.get("/stats")
async def get_public_stats(db: Session = Depends(get_db)):
    """
    Get statistics about public documents
    
    Returns summary statistics about publicly shared documents.
    """
    try:
        total_public_docs = db.query(Document).filter(Document.is_public == True).count()
        total_shares = db.query(PublicShare).count()
        
        # Count by file type
        file_type_stats = {}
        public_docs = db.query(Document).filter(Document.is_public == True).all()
        
        for doc in public_docs:
            file_type = doc.file_type
            if file_type in file_type_stats:
                file_type_stats[file_type] += 1
            else:
                file_type_stats[file_type] = 1
        
        return {
            "total_public_documents": total_public_docs,
            "total_shares": total_shares,
            "file_type_distribution": file_type_stats,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get public stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get public statistics")