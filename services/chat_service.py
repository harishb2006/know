import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import google.generativeai as genai

from app.database import get_db_sync
from app.models import Conversation
from app.config import settings
from .document_service import DocumentService

logger = logging.getLogger(__name__)

class ChatService:
    """Enhanced chat service with source attribution and reasoning"""
    
    def __init__(self):
        """Initialize the chat service"""
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.document_service = DocumentService()
            logger.info("Chat service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize chat service: {e}")
            raise
    
    async def chat_with_context(
        self, 
        message: str, 
        session_id: str,
        mode: str = "chat",
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """
        Chat with AI using document context and provide detailed source attribution
        
        Args:
            message: User's question/message
            session_id: Conversation session ID
            mode: Chat mode (chat, summarize, insights, planning)
            max_sources: Maximum number of source documents to include
        """
        try:
            # Step 1: Search for relevant documents
            logger.info(f"Searching for relevant documents for query: {message[:100]}...")
            search_results = self.document_service.search_documents(message, k=max_sources)
            
            # Step 2: Build context from search results
            context_info = self._build_context_from_sources(search_results)
            
            # Step 3: Generate AI response with source attribution
            ai_response_data = await self._generate_response_with_attribution(
                message, context_info, mode
            )
            
            # Step 4: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                search_results, ai_response_data
            )
            
            # Step 5: Save conversation to database
            conversation_id = self._save_conversation(
                session_id=session_id,
                user_message=message,
                ai_response=ai_response_data['response'],
                mode=mode,
                sources_used=search_results,
                confidence_score=confidence_score
            )
            
            # Step 6: Format final response
            return {
                'conversation_id': conversation_id,
                'response': ai_response_data['response'],
                'reasoning': ai_response_data['reasoning'],
                'sources': self._format_sources_for_response(search_results),
                'confidence_score': confidence_score,
                'context_summary': context_info['summary'],
                'mode': mode,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            return {
                'error': str(e),
                'response': "I apologize, but I encountered an error while processing your request. Please try again.",
                'sources': [],
                'confidence_score': 0.0
            }
    
    def _build_context_from_sources(self, search_results: List[Dict]) -> Dict[str, Any]:
        """Build comprehensive context from search results"""
        if not search_results:
            return {
                'context_text': "No relevant documents found.",
                'summary': "No context available",
                'total_sources': 0
            }
        
        context_chunks = []
        document_summaries = {}
        
        for result in search_results:
            # Add chunk content with metadata
            chunk_info = f"""
Source: {result['document_name']} (Chunk {result['chunk_index'] + 1})
Relevance: {result['similarity_score']:.2f}
Content: {result['chunk_content']}
---
"""
            context_chunks.append(chunk_info)
            
            # Track document summaries
            doc_id = result['document_id']
            if doc_id not in document_summaries:
                document_summaries[doc_id] = {
                    'name': result['document_name'],
                    'chunks_used': 0,
                    'avg_relevance': 0.0
                }
            
            document_summaries[doc_id]['chunks_used'] += 1
            document_summaries[doc_id]['avg_relevance'] += result['similarity_score']
        
        # Calculate average relevance for each document
        for doc_id in document_summaries:
            doc_info = document_summaries[doc_id]
            doc_info['avg_relevance'] /= doc_info['chunks_used']
        
        context_text = "\n".join(context_chunks)
        
        summary = f"Found {len(search_results)} relevant text segments from {len(document_summaries)} documents."
        
        return {
            'context_text': context_text,
            'summary': summary,
            'total_sources': len(search_results),
            'document_summaries': document_summaries
        }
    
    async def _generate_response_with_attribution(
        self, 
        user_message: str, 
        context_info: Dict[str, Any], 
        mode: str
    ) -> Dict[str, Any]:
        """Generate AI response with detailed reasoning and source attribution"""
        
        # Build prompt based on mode
        if mode == "summarize":
            system_prompt = self._get_summarize_prompt()
        elif mode == "insights":
            system_prompt = self._get_insights_prompt()
        elif mode == "planning":
            system_prompt = self._get_planning_prompt()
        else:  # default chat mode
            system_prompt = self._get_chat_prompt()
        
        # Construct the full prompt
        full_prompt = f"""
{system_prompt}

CONTEXT FROM DOCUMENTS:
{context_info['context_text']}

USER QUESTION: {user_message}

Please provide:
1. A comprehensive answer to the user's question
2. Clear reasoning for your response
3. Specific references to the source documents used
4. Confidence indicators for different parts of your answer

Response format should be natural and conversational while being thorough and well-sourced.
"""
        
        try:
            # Generate response using Gemini
            response = await self.model.generate_content_async(full_prompt)
            response_text = response.text
            
            # Extract reasoning (this is a simplified approach - in production you might want more sophisticated parsing)
            reasoning = self._extract_reasoning_from_response(response_text, context_info)
            
            return {
                'response': response_text,
                'reasoning': reasoning
            }
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return {
                'response': "I apologize, but I'm having trouble generating a response right now. Please try again.",
                'reasoning': "Error in AI response generation"
            }
    
    def _get_chat_prompt(self) -> str:
        """Get system prompt for chat mode"""
        return """
You are an intelligent Knowledge Assistant that helps users find and understand information from their uploaded documents.

CORE PRINCIPLES:
- Always base your answers on the provided document context
- Be transparent about what information comes from which sources
- Explain your reasoning clearly
- If information is not in the documents, clearly state this
- Provide confidence levels for different parts of your answer
- Use natural, conversational language while being thorough

RESPONSE GUIDELINES:
- Start with a direct answer to the user's question
- Support your answer with specific references to the source documents
- Explain any connections or insights you draw from the information
- Mention any limitations or gaps in the available information
- Suggest related topics or follow-up questions when appropriate
"""
    
    def _get_summarize_prompt(self) -> str:
        """Get system prompt for summarize mode"""
        return """
You are summarizing information from multiple documents. 

SUMMARIZATION GUIDELINES:
- Create a comprehensive yet concise summary
- Organize information logically with clear sections
- Highlight key points and main themes
- Note any conflicting information between sources
- Include confidence levels for different summary points
- Reference specific documents for major claims
"""
    
    def _get_insights_prompt(self) -> str:
        """Get system prompt for insights mode"""
        return """
You are analyzing documents to provide insights and patterns.

INSIGHT GUIDELINES:
- Look for patterns, trends, and connections across documents
- Identify key themes and recurring topics
- Point out notable similarities or differences
- Suggest implications and potential conclusions
- Highlight areas that might need further investigation
- Base all insights on evidence from the provided documents
"""
    
    def _get_planning_prompt(self) -> str:
        """Get system prompt for planning mode"""
        return """
You are helping with planning and decision-making based on document information.

PLANNING GUIDELINES:
- Identify actionable items and next steps
- Suggest priorities based on the information available
- Point out potential risks or considerations
- Recommend additional information that might be needed
- Provide structured, practical recommendations
- Base all suggestions on evidence from the documents
"""
    
    def _extract_reasoning_from_response(self, response_text: str, context_info: Dict) -> str:
        """Extract reasoning explanation from AI response"""
        # This is a simplified approach - in a production system you might:
        # 1. Use a separate AI call to generate reasoning
        # 2. Parse the response for specific reasoning sections
        # 3. Use prompt engineering to get structured reasoning output
        
        reasoning_parts = [
            f"Based on {context_info['total_sources']} relevant text segments",
            f"Context summary: {context_info['summary']}",
            "Response generated using document context and AI analysis"
        ]
        
        return " | ".join(reasoning_parts)
    
    def _calculate_confidence_score(
        self, 
        search_results: List[Dict], 
        ai_response_data: Dict
    ) -> float:
        """Calculate confidence score for the response"""
        if not search_results:
            return 0.1  # Very low confidence without sources
        
        # Factors affecting confidence:
        # 1. Average similarity score of sources
        # 2. Number of sources
        # 3. Response quality indicators
        
        avg_similarity = sum(r['similarity_score'] for r in search_results) / len(search_results)
        source_count_factor = min(len(search_results) / 5.0, 1.0)  # Normalized to max of 5 sources
        
        # Basic confidence calculation
        confidence = (avg_similarity * 0.7 + source_count_factor * 0.3)
        
        return round(confidence, 2)
    
    def _format_sources_for_response(self, search_results: List[Dict]) -> List[Dict]:
        """Format sources for the API response"""
        formatted_sources = []
        
        for i, result in enumerate(search_results):
            formatted_sources.append({
                'id': i + 1,
                'document_name': result['document_name'],
                'document_id': result['document_id'],
                'relevance_score': result['similarity_score'],
                'chunk_index': result['chunk_index'],
                'content_preview': result['chunk_content'][:200] + "..." if len(result['chunk_content']) > 200 else result['chunk_content'],
                'page_number': result.get('page_number'),
                'is_public': result.get('is_public', False)
            })
        
        return formatted_sources
    
    def _save_conversation(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        mode: str,
        sources_used: List[Dict],
        confidence_score: float
    ) -> str:
        """Save conversation to database"""
        try:
            db = get_db_sync()
            
            conversation = Conversation(
                session_id=session_id,
                user_message=user_message,
                ai_response=ai_response,
                mode=mode,
                sources_used=[
                    {
                        'document_id': s['document_id'],
                        'document_name': s['document_name'],
                        'similarity_score': s['similarity_score'],
                        'chunk_index': s['chunk_index']
                    }
                    for s in sources_used
                ],
                confidence_score=confidence_score
            )
            
            db.add(conversation)
            db.commit()
            
            conversation_id = conversation.id
            db.close()
            
            return conversation_id
            
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return "unknown"
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            db = get_db_sync()
            
            conversations = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).order_by(Conversation.created_at.desc()).limit(limit).all()
            
            history = []
            for conv in conversations:
                history.append({
                    'id': conv.id,
                    'user_message': conv.user_message,
                    'ai_response': conv.ai_response,
                    'mode': conv.mode,
                    'sources_used': conv.sources_used,
                    'confidence_score': conv.confidence_score,
                    'created_at': conv.created_at.isoformat()
                })
            
            db.close()
            return history
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []