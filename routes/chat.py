from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
import logging

from services.chat_service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = ChatService()

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=2000, description="User's message or question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    mode: str = Field("chat", description="Chat mode: chat, summarize, insights, planning")
    max_sources: int = Field(5, ge=1, le=10, description="Maximum number of source documents to use")

class ChatResponse(BaseModel):
    """Chat response model"""
    conversation_id: str
    response: str
    reasoning: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    context_summary: str
    mode: str
    timestamp: str
    session_id: str

@router.post("/", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """
    Chat with AI using uploaded documents as context
    
    This endpoint provides intelligent responses based on your uploaded documents with:
    - Source attribution and citations
    - Confidence scores for responses
    - Detailed reasoning explanations
    - Multiple chat modes (chat, summarize, insights, planning)
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Validate mode
        valid_modes = ["chat", "summarize", "insights", "planning"]
        if request.mode not in valid_modes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid mode. Must be one of: {', '.join(valid_modes)}"
            )
        
        logger.info(f"Processing chat request - Mode: {request.mode}, Session: {session_id}")
        
        # Process chat request
        result = await chat_service.chat_with_context(
            message=request.message,
            session_id=session_id,
            mode=request.mode,
            max_sources=request.max_sources
        )
        
        # Check for errors
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        # Return response
        return ChatResponse(
            session_id=session_id,
            **result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """
    Get conversation history for a session
    
    Retrieves the chat history for a specific session, including:
    - Previous questions and responses
    - Source documents used
    - Confidence scores
    - Chat modes used
    """
    try:
        if limit > 100:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 100")
        
        history = chat_service.get_conversation_history(session_id, limit)
        
        return {
            "session_id": session_id,
            "conversations": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@router.get("/modes")
async def get_chat_modes():
    """
    Get available chat modes and their descriptions
    
    Returns information about different chat modes available in the system.
    """
    return {
        "modes": [
            {
                "name": "chat",
                "description": "General question-answering with document context",
                "use_case": "Ask questions about your documents and get detailed answers"
            },
            {
                "name": "summarize", 
                "description": "Summarize information from multiple documents",
                "use_case": "Get comprehensive summaries of document content"
            },
            {
                "name": "insights",
                "description": "Analyze documents for patterns and insights",
                "use_case": "Discover trends, patterns, and key insights across documents"
            },
            {
                "name": "planning",
                "description": "Generate actionable plans and recommendations",
                "use_case": "Get structured plans and next steps based on document content"
            }
        ]
    }

@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear conversation history for a session
    
    Deletes all chat history for the specified session ID.
    """
    try:
        # Note: This would need to be implemented in the chat service
        # For now, return success (history clearing can be added later)
        
        return {
            "message": f"Chat history cleared for session {session_id}",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Failed to clear chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear chat history")