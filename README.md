# 🧠 Knowledge Assistant

A powerful AI-powered document management and chat system that provides intelligent answers with source attribution and detailed reasoning.

## ✨ Features

### 📄 Document Processing
- **Multi-format support**: PDF, DOCX, images (JPG, PNG, TIFF), plain text
- **Advanced OCR**: Extract text from images with confidence scoring
- **Smart chunking**: Automatic text segmentation for optimal search
- **Vector embeddings**: Semantic search using Google's Gemini AI

### 💬 Intelligent Chat
- **Context-aware responses**: AI answers based on your documents
- **Source attribution**: Every answer includes source citations
- **Confidence scoring**: Know how reliable each response is
- **Multiple modes**: Chat, summarize, insights, and planning modes
- **Detailed reasoning**: Understand how the AI reached its conclusions

### 🔗 Public Sharing
- **Secure sharing**: Generate public links for documents
- **Expiration controls**: Set time limits on shared documents
- **Public browsing**: Explore publicly available documents
- **File viewer**: Built-in support for viewing different file types

### 🏗️ Technical Stack
- **Backend**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with vector operations
- **AI**: Google Gemini AI for embeddings and chat
- **OCR**: Tesseract for image text extraction
- **Containerization**: Docker and Docker Compose

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Docker and Docker Compose
- Git
- A Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd py_fast

# Run the automated setup script
./setup.sh
```

The setup script will:
- Install system dependencies
- Create Python virtual environment
- Install Python packages
- Setup environment variables
- Start database services
- Create database tables

### 2. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv postgresql-client tesseract-ocr docker.io docker-compose

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env file and add your GEMINI_API_KEY

# 5. Start services
docker-compose up -d postgres redis

# 6. Create uploads directory
mkdir -p uploads
```

### 3. Start the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Start the backend server
python main.py
```

The API will be available at:
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 API Usage

### Upload a Document
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-document.pdf" \
  -F "is_public=false"
```

### Search Documents
```bash
curl -X GET "http://localhost:8000/api/documents/search?query=your%20search%20query&k=5"
```

### Chat with Documents
```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main topics in my documents?",
    "mode": "chat",
    "max_sources": 5
  }'
```

### Create Public Share
```bash
curl -X POST "http://localhost:8000/api/public/share" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "your-document-id",
    "expires_in_days": 30
  }'
```

## 🗂️ Project Structure

```
py_fast/
├── 📄 main.py                 # FastAPI application entry point
├── 🐳 docker-compose.yml      # Docker services configuration
├── 📦 requirements.txt        # Python dependencies
├── 🔧 .env.example           # Environment variables template
├── 🚀 setup.sh               # Automated setup script
├── 📖 README.md              # This file
├── 
├── 📁 app/                   # Core application code
│   ├── 🗄️  database.py       # Database connection and session management
│   ├── 📋 models.py          # SQLAlchemy database models
│   └── ⚙️  config.py         # Application configuration
├── 
├── 📁 routes/                # API endpoints
│   ├── 📄 documents.py       # Document upload and search endpoints
│   ├── 💬 chat.py            # Chat and AI interaction endpoints
│   └── 🔗 public.py          # Public sharing endpoints
├── 
├── 📁 services/              # Business logic
│   ├── 📄 document_service.py # Document processing and search
│   ├── 🧠 embedding_service.py # Vector embedding generation
│   ├── 💬 chat_service.py     # AI chat with source attribution
│   └── 👁️  ocr_service.py     # OCR text extraction
└── 
└── 📁 uploads/              # Uploaded files storage
```

## 📊 Database Models

### Document
Stores uploaded file information and extracted content.
```sql
- id (UUID): Unique document identifier
- filename (String): Original filename
- file_type (String): File extension (pdf, docx, jpg, etc.)
- content (Text): Extracted text content
- file_size (Integer): File size in bytes
- is_public (Boolean): Whether document is publicly accessible
- metadata (JSON): Processing details, OCR confidence, etc.
- created_at/updated_at (DateTime): Timestamps
```

### DocumentChunk
Text segments for vector search and source attribution.
```sql
- id (UUID): Unique chunk identifier
- document_id (UUID): Reference to parent document
- content (Text): Chunk text content
- chunk_index (Integer): Order within document
- start_char/end_char (Integer): Position in original text
- page_number (Integer): Page reference for PDFs
- embedding (JSON): Vector embedding for similarity search
```

### Conversation
Chat history with AI responses and source tracking.
```sql
- id (UUID): Unique conversation identifier
- session_id (String): Group related conversations
- user_message (Text): User's question
- ai_response (Text): AI's answer
- mode (String): Chat mode used (chat, summarize, insights, planning)
- sources_used (JSON): Documents and chunks referenced
- confidence_score (Float): Response reliability score
- created_at (DateTime): Timestamp
```

### PublicShare
Manage public document sharing with secure tokens.
```sql
- id (UUID): Unique share identifier
- document_id (UUID): Reference to shared document
- share_token (String): Secure access token
- created_at (DateTime): When share was created
- expires_at (DateTime): Optional expiration time
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_assistant

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
FRONTEND_URL=http://localhost:3000

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# AI Model Settings
EMBEDDING_MODEL=models/embedding-001
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## 🤖 AI Features

### Chat Modes

1. **Chat Mode** (`mode: "chat"`)
   - General question-answering
   - Context-aware responses
   - Source attribution for all claims

2. **Summarize Mode** (`mode: "summarize"`)
   - Comprehensive document summaries
   - Key point extraction
   - Multi-document synthesis

3. **Insights Mode** (`mode: "insights"`)
   - Pattern recognition across documents
   - Trend analysis
   - Connection discovery

4. **Planning Mode** (`mode: "planning"`)
   - Actionable recommendations
   - Next steps generation
   - Risk assessment

### Source Attribution

Every AI response includes:
- **Source citations**: Specific document references
- **Relevance scores**: How well sources match the query
- **Content previews**: Snippets from source material
- **Confidence indicators**: Reliability assessment
- **Reasoning explanation**: How the AI reached its conclusion

## 🚀 Deployment

### Development
```bash
# Start all services
docker-compose up -d

# Run backend in development mode
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Or build custom image
docker build -t knowledge-assistant .
docker run -p 8000:8000 --env-file .env knowledge-assistant
```

## 🛠️ Development

### Adding New Features

1. **New API Endpoints**: Add routes in `routes/` directory
2. **Database Changes**: Update models in `app/models.py`
3. **Business Logic**: Implement in `services/` directory
4. **Dependencies**: Update `requirements.txt`

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 🔒 Security

- Secure file upload validation
- SQL injection prevention with SQLAlchemy
- Input sanitization and validation
- Secure token generation for public shares
- Environment variable protection

## 📈 Performance

- Vector similarity search with optimized indexing
- Database connection pooling
- Efficient text chunking algorithms
- Background task processing with Celery
- Caching with Redis

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # View logs
   docker-compose logs postgres
   ```

2. **OCR Not Working**
   ```bash
   # Install Tesseract
   sudo apt-get install tesseract-ocr tesseract-ocr-eng
   
   # Check installation
   tesseract --version
   ```

3. **Gemini API Errors**
   - Verify API key in `.env` file
   - Check API quota and billing
   - Ensure network connectivity

4. **File Upload Errors**
   - Check file size limits
   - Verify file type support
   - Ensure uploads directory exists and is writable

### Logs

```bash
# View application logs
docker-compose logs backend

# View database logs
docker-compose logs postgres

# View all logs
docker-compose logs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful embeddings and chat capabilities
- **FastAPI** for the excellent web framework
- **Tesseract** for OCR functionality
- **PostgreSQL** for robust data storage
- **Docker** for containerization

## 📞 Support

For questions, issues, or feature requests, please:
1. Check the [troubleshooting guide](#-troubleshooting)
2. Search existing [issues](../../issues)
3. Create a new issue with detailed information

---

**Happy Knowledge Managing! 🧠✨**# know
