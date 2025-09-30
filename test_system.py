#!/usr/bin/env python3
"""
Knowledge Assistant Test Script
This script tests the main functionality of the Knowledge Assistant system.
"""

import os
import sys
import asyncio
import json
import requests
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_api_connection():
    """Test if the API server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API server: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_gemini_api():
    """Test Gemini API configuration"""
    try:
        from app.config import settings
        
        if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
            print("⚠️  Gemini API key not configured")
            return False
        
        # Test basic embedding generation
        from services.embedding_service import EmbeddingService
        
        embedding_service = EmbeddingService()
        embedding = embedding_service.generate_embedding("test text")
        
        if embedding is not None:
            print("✅ Gemini API working")
            return True
        else:
            print("❌ Gemini API test failed")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return False

def test_ocr_service():
    """Test OCR functionality"""
    try:
        from services.ocr_service import OCRService
        
        # Create a simple test image (this is just a basic test)
        ocr_service = OCRService()
        print("✅ OCR service initialized")
        return True
        
    except Exception as e:
        print(f"❌ OCR service error: {e}")
        return False

def test_file_uploads():
    """Test file upload functionality"""
    try:
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Test if directory is writable
        test_file = uploads_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        
        print("✅ File upload directory accessible")
        return True
        
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
        return False

def create_test_document():
    """Create a test document for testing"""
    test_content = """
    # Test Document for Knowledge Assistant
    
    This is a test document to verify the Knowledge Assistant functionality.
    
    ## Key Features
    - Document processing and text extraction
    - Vector embeddings for semantic search
    - AI-powered chat with source attribution
    - Public document sharing
    
    ## Technology Stack
    - FastAPI for the backend API
    - PostgreSQL for data storage
    - Google Gemini AI for embeddings and chat
    - Tesseract OCR for image text extraction
    
    This document contains information about artificial intelligence,
    machine learning, and document processing systems.
    """
    
    test_file = Path("test_document.txt")
    test_file.write_text(test_content)
    return test_file

def test_document_upload():
    """Test document upload via API"""
    if not test_api_connection():
        return False
    
    try:
        # Create test document
        test_file = create_test_document()
        
        # Upload document
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'text/plain')}
            data = {'is_public': 'true'}
            
            response = requests.post(
                "http://localhost:8000/api/documents/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        # Clean up test file
        test_file.unlink()
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Document upload successful: {result.get('document_id')}")
                return result.get('document_id')
            else:
                print(f"❌ Document upload failed: {result.get('error')}")
                return None
        else:
            print(f"❌ Document upload failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Document upload test error: {e}")
        return None

def test_document_search():
    """Test document search functionality"""
    if not test_api_connection():
        return False
    
    try:
        response = requests.get(
            "http://localhost:8000/api/documents/search",
            params={'query': 'artificial intelligence', 'k': 3},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document search successful: found {len(result.get('results', []))} results")
            return True
        else:
            print(f"❌ Document search failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Document search test error: {e}")
        return False

def test_chat_functionality():
    """Test AI chat functionality"""
    if not test_api_connection():
        return False
    
    try:
        chat_data = {
            "message": "What is artificial intelligence?",
            "mode": "chat",
            "max_sources": 3
        }
        
        response = requests.post(
            "http://localhost:8000/api/chat/",
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat functionality successful")
            print(f"   Response preview: {result.get('response', '')[:100]}...")
            print(f"   Sources used: {len(result.get('sources', []))}")
            print(f"   Confidence: {result.get('confidence_score', 0):.2f}")
            return True
        else:
            print(f"❌ Chat test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Chat test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧠 Knowledge Assistant Test Suite")
    print("=" * 40)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("File Upload Directory", test_file_uploads),
        ("OCR Service", test_ocr_service),
        ("Gemini API", test_gemini_api),
        ("API Server", test_api_connection),
    ]
    
    # Run basic tests
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Basic Tests: {passed}/{total} passed")
    
    # Run integration tests if basic tests pass
    if passed == total:
        print("\n🚀 Running Integration Tests...")
        
        integration_tests = [
            ("Document Upload", test_document_upload),
            ("Document Search", test_document_search),
            ("Chat Functionality", test_chat_functionality),
        ]
        
        integration_passed = 0
        for test_name, test_func in integration_tests:
            print(f"\n🔍 Testing {test_name}...")
            if test_func():
                integration_passed += 1
        
        print(f"\n📊 Integration Tests: {integration_passed}/{len(integration_tests)} passed")
        
        if integration_passed == len(integration_tests):
            print("\n🎉 All tests passed! Knowledge Assistant is working correctly.")
        else:
            print("\n⚠️  Some integration tests failed. Check the configuration.")
    else:
        print("\n⚠️  Basic tests failed. Please check the setup.")
    
    print("\n" + "=" * 40)
    print("Test complete!")

if __name__ == "__main__":
    main()