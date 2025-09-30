import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test configuration
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)

@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal()
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_file():
    """Create test file for upload"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document for Knowledge Assistant testing.")
        f.write("\n\nIt contains multiple lines of text for testing purposes.")
        f.write("\n\nThis helps verify document processing functionality.")
        temp_path = f.name
    
    yield temp_path
    os.unlink(temp_path)

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Knowledge Assistant" in response.json()["message"]
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestDocumentUpload:
    """Test document upload functionality"""
    
    def test_upload_text_file(self, client, test_file):
        with open(test_file, 'rb') as f:
            response = client.post(
                "/api/documents/upload",
                files={"file": ("test.txt", f, "text/plain")},
                data={"is_public": "false"}
            )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "document_id" in result
        assert result["filename"] == "test.txt"
    
    def test_upload_large_file(self, client):
        # Create a file larger than allowed size
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"x" * (11 * 1024 * 1024))  # 11MB
            f.seek(0)
            
            response = client.post(
                "/api/documents/upload",
                files={"file": ("large.txt", f, "text/plain")},
                data={"is_public": "false"}
            )
        
        assert response.status_code == 413
    
    def test_upload_unsupported_file_type(self, client):
        with tempfile.NamedTemporaryFile(suffix='.exe') as f:
            f.write(b"fake executable")
            f.seek(0)
            
            response = client.post(
                "/api/documents/upload",
                files={"file": ("test.exe", f, "application/octet-stream")},
                data={"is_public": "false"}
            )
        
        assert response.status_code == 400

class TestDocumentSearch:
    """Test document search functionality"""
    
    def test_search_documents(self, client):
        response = client.get("/api/documents/search?query=test&k=5")
        assert response.status_code == 200
        result = response.json()
        assert "query" in result
        assert "results" in result
        assert result["query"] == "test"
    
    def test_search_empty_query(self, client):
        response = client.get("/api/documents/search?query=&k=5")
        assert response.status_code == 400
    
    def test_search_invalid_k(self, client):
        response = client.get("/api/documents/search?query=test&k=25")
        assert response.status_code == 400

class TestChatFunctionality:
    """Test AI chat functionality"""
    
    def test_chat_endpoint(self, client):
        chat_data = {
            "message": "What is artificial intelligence?",
            "mode": "chat",
            "max_sources": 3
        }
        
        response = client.post("/api/chat/", json=chat_data)
        assert response.status_code == 200
        result = response.json()
        assert "response" in result
        assert "sources" in result
        assert "confidence_score" in result
    
    def test_chat_invalid_mode(self, client):
        chat_data = {
            "message": "Test message",
            "mode": "invalid_mode",
            "max_sources": 3
        }
        
        response = client.post("/api/chat/", json=chat_data)
        assert response.status_code == 400
    
    def test_chat_modes(self, client):
        response = client.get("/api/chat/modes")
        assert response.status_code == 200
        result = response.json()
        assert "modes" in result
        assert len(result["modes"]) == 4

class TestPublicSharing:
    """Test public document sharing"""
    
    def test_public_document_list(self, client):
        response = client.get("/api/public/list")
        assert response.status_code == 200
        result = response.json()
        assert "documents" in result
        assert "total" in result
    
    def test_public_stats(self, client):
        response = client.get("/api/public/stats")
        assert response.status_code == 200
        result = response.json()
        assert "total_public_documents" in result
        assert "file_type_distribution" in result

class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self, client, test_file):
        """Test complete workflow: upload -> search -> chat"""
        
        # 1. Upload document
        with open(test_file, 'rb') as f:
            upload_response = client.post(
                "/api/documents/upload",
                files={"file": ("workflow_test.txt", f, "text/plain")},
                data={"is_public": "true"}
            )
        
        assert upload_response.status_code == 200
        upload_result = upload_response.json()
        document_id = upload_result["document_id"]
        
        # 2. Search for the document
        search_response = client.get("/api/documents/search?query=test document&k=5")
        assert search_response.status_code == 200
        
        # 3. Chat about the document
        chat_data = {
            "message": "What does the test document contain?",
            "mode": "chat",
            "max_sources": 3
        }
        
        chat_response = client.post("/api/chat/", json=chat_data)
        assert chat_response.status_code == 200
        
        # 4. Create public share
        share_data = {
            "document_id": document_id,
            "expires_in_days": 30
        }
        
        share_response = client.post("/api/public/share", json=share_data)
        assert share_response.status_code == 200
        share_result = share_response.json()
        assert "share_token" in share_result

# Performance tests
class TestPerformance:
    """Performance and load tests"""
    
    def test_concurrent_uploads(self, client):
        """Test multiple concurrent uploads"""
        import concurrent.futures
        import threading
        
        def upload_file():
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as f:
                f.write(f"Test content {threading.current_thread().ident}")
                f.flush()
                
                with open(f.name, 'rb') as upload_file:
                    response = client.post(
                        "/api/documents/upload",
                        files={"file": ("concurrent_test.txt", upload_file, "text/plain")},
                        data={"is_public": "false"}
                    )
                return response.status_code
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(upload_file) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Most uploads should succeed
        success_count = sum(1 for status in results if status == 200)
        assert success_count >= 3  # Allow some failures under load

# Database tests
class TestDatabase:
    """Test database operations"""
    
    def test_database_models(self, test_db):
        """Test database model creation and relationships"""
        from app.models import Document, DocumentChunk, Conversation
        
        # Create a document
        document = Document(
            filename="test.txt",
            file_type="txt",
            content="Test content",
            file_size=100,
            is_public=False
        )
        
        test_db.add(document)
        test_db.commit()
        
        # Verify document was created
        assert document.id is not None
        
        # Create a chunk
        chunk = DocumentChunk(
            document_id=document.id,
            content="Test chunk",
            chunk_index=0,
            start_char=0,
            end_char=10
        )
        
        test_db.add(chunk)
        test_db.commit()
        
        # Verify relationships
        assert len(document.chunks) == 1
        assert chunk.document.id == document.id

if __name__ == "__main__":
    pytest.main([__file__, "-v"])