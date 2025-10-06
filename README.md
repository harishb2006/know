# 🧠 Knowledge Assistant# 🧠 Knowledge Assistant



An intelligent document management and AI-powered Q&A system built with FastAPI, React TypeScript, and Google Gemini AI.A powerful AI-powered document management and chat system that provides intelligent answers with source attribution and detailed reasoning.



## ✨ Features## ✨ Features



- **🔐 User Authentication** - Secure JWT-based authentication### 📄 Document Processing

- **📄 Document Upload** - Support for PDF, TXT, DOCX files with drag-and-drop- **Multi-format support**: PDF, DOCX, images (JPG, PNG, TIFF), plain text

- **💬 Chat Upload** - Process chat conversations from various platforms- **Advanced OCR**: Extract text from images with confidence scoring

- **🤖 AI-Powered Q&A** - Ask questions about your documents using Gemini AI- **Smart chunking**: Automatic text segmentation for optimal search

- **🔍 Vector Search** - Intelligent document retrieval using ChromaDB- **Vector embeddings**: Semantic search using Google's Gemini AI

- **📊 Document Management** - Organize, search, and filter your documents

- **🎨 Modern UI** - Beautiful React TypeScript interface with Tailwind CSS### 💬 Intelligent Chat

- **Context-aware responses**: AI answers based on your documents

## 🏗️ Tech Stack- **Source attribution**: Every answer includes source citations

- **Confidence scoring**: Know how reliable each response is

### Backend- **Multiple modes**: Chat, summarize, insights, and planning modes

- **FastAPI** - High-performance Python web framework- **Detailed reasoning**: Understand how the AI reached its conclusions

- **MongoDB Atlas** - Cloud database for user and document management

- **ChromaDB** - Vector database for document embeddings### 🔗 Public Sharing

- **Google Gemini 2.0 Flash** - AI model for text generation and embeddings- **Secure sharing**: Generate public links for documents

- **JWT Authentication** - Secure token-based authentication- **Expiration controls**: Set time limits on shared documents

- **Argon2** - Password hashing- **Public browsing**: Explore publicly available documents

- **File viewer**: Built-in support for viewing different file types

### Frontend

- **React 19** - Modern React with latest features### 🏗️ Technical Stack

- **TypeScript** - Type-safe development- **Backend**: FastAPI with Python 3.11+

- **Vite** - Fast development and build tool- **Database**: PostgreSQL with vector operations

- **Tailwind CSS v4** - Utility-first CSS framework- **AI**: Google Gemini AI for embeddings and chat

- **React Router** - Client-side routing- **OCR**: Tesseract for image text extraction

- **Axios** - HTTP client for API calls- **Containerization**: Docker and Docker Compose

- **Lucide Icons** - Beautiful icon library

## 🚀 Quick Start

## 📋 Prerequisites

### Prerequisites

- **Python 3.8+**- Python 3.11 or higher

- **Node.js 16+**- Docker and Docker Compose

- **npm or yarn**- Git

- **MongoDB Atlas account**- A Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

- **Google Gemini API key**

### 1. Clone and Setup

## 🚀 Quick Start```bash

git clone <your-repo-url>

### 1. Clone the Repositorycd py_fast

```bash

git clone https://github.com/harishb2006/know.git# Run the automated setup script

cd know./setup.sh

``````



### 2. Run SetupThe setup script will:

```bash- Install system dependencies

./scripts/setup.sh- Create Python virtual environment

```- Install Python packages

- Setup environment variables

### 3. Configure Environment- Start database services

Edit `.env` file with your credentials:- Create database tables

```env

# Gemini AI Configuration### 2. Manual Setup (Alternative)

GEMINI_API_KEY=your_gemini_api_key_here

If you prefer manual setup:

# MongoDB Configuration

MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/knowledge_db```bash

# 1. Install system dependencies (Ubuntu/Debian)

# JWT Configurationsudo apt-get update

JWT_SECRET_KEY=your_super_secret_jwt_key_heresudo apt-get install -y python3 python3-pip python3-venv postgresql-client tesseract-ocr docker.io docker-compose

JWT_ALGORITHM=HS256

JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30# 2. Create virtual environment

```python3 -m venv venv

source venv/bin/activate

### 4. Start the Application

```bash# 3. Install Python dependencies

./scripts/start.shpip install -r requirements.txt

```

# 4. Setup environment

### 5. Access the Applicationcp .env.example .env

- **Frontend**: http://localhost:5177# Edit .env file and add your GEMINI_API_KEY

- **Backend API**: http://localhost:8000

- **API Documentation**: http://localhost:8000/docs# 5. Start services

docker-compose up -d postgres redis

## 📁 Project Structure

# 6. Create uploads directory

```mkdir -p uploads

knowledge-assistant/```

├── backend/                 # FastAPI backend

│   ├── api/                # API route handlers### 3. Start the Application

│   ├── models/             # Pydantic models and auth

│   ├── services/           # Business logic and utilities```bash

│   │   ├── database.py     # MongoDB connection# Activate virtual environment

│   │   ├── vectorstore.py  # ChromaDB integrationsource venv/bin/activate

│   │   └── utils.py        # Document processing

│   ├── main.py            # FastAPI application# Start the backend server

│   └── __init__.pypython main.py

├── frontend/               # React TypeScript frontend```

│   ├── public/            # Static assets

│   ├── src/The API will be available at:

│   │   ├── components/    # React components- **API Server**: http://localhost:8000

│   │   │   ├── Auth/      # Authentication components- **API Documentation**: http://localhost:8000/docs

│   │   │   └── Dashboard/ # Main app components- **Health Check**: http://localhost:8000/health

│   │   ├── services/      # API service layer

│   │   ├── types/         # TypeScript type definitions## 📚 API Usage

│   │   └── main.tsx       # Application entry point

│   ├── package.json### Upload a Document

│   └── vite.config.ts```bash

├── scripts/               # Utility scriptscurl -X POST "http://localhost:8000/api/documents/upload" \

│   ├── setup.sh          # Development setup  -H "Content-Type: multipart/form-data" \

│   └── start.sh          # Application startup  -F "file=@your-document.pdf" \

├── uploads/              # Document storage  -F "is_public=false"

├── chroma_db/           # Vector database files```

├── requirements.txt     # Python dependencies

├── .env.example        # Environment template### Search Documents

└── README.md```bash

```curl -X GET "http://localhost:8000/api/documents/search?query=your%20search%20query&k=5"

```

## 🛠️ API Endpoints

### Chat with Documents

### Authentication```bash

- `POST /register` - Register new usercurl -X POST "http://localhost:8000/api/chat/" \

- `POST /login` - User login  -H "Content-Type: application/json" \

- `GET /me` - Get current user info  -d '{

    "message": "What are the main topics in my documents?",

### Documents    "mode": "chat",

- `POST /upload` - Upload document    "max_sources": 5

- `GET /documents` - List user documents  }'

- `DELETE /documents/{doc_id}` - Delete document```



### Chat### Create Public Share

- `POST /upload-chat` - Upload chat conversation```bash

curl -X POST "http://localhost:8000/api/public/share" \

### AI Q&A  -H "Content-Type: application/json" \

- `POST /ask` - Ask questions about documents  -d '{

    "document_id": "your-document-id",

## 🔧 Development    "expires_in_days": 30

  }'

### Backend Development```

```bash

# Activate virtual environment## 🗂️ Project Structure

source venv/bin/activate

```

# Run backend server with auto-reloadpy_fast/

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload├── 📄 main.py                 # FastAPI application entry point

```├── 🐳 docker-compose.yml      # Docker services configuration

├── 📦 requirements.txt        # Python dependencies

### Frontend Development├── 🔧 .env.example           # Environment variables template

```bash├── 🚀 setup.sh               # Automated setup script

# Navigate to frontend directory├── 📖 README.md              # This file

cd frontend├── 

├── 📁 app/                   # Core application code

# Start development server│   ├── 🗄️  database.py       # Database connection and session management

npm run dev│   ├── 📋 models.py          # SQLAlchemy database models

```│   └── ⚙️  config.py         # Application configuration

├── 

## 🔒 Security├── 📁 routes/                # API endpoints

│   ├── 📄 documents.py       # Document upload and search endpoints

- **JWT Authentication**: Secure token-based authentication│   ├── 💬 chat.py            # Chat and AI interaction endpoints

- **Password Hashing**: Argon2 for secure password storage│   └── 🔗 public.py          # Public sharing endpoints

- **CORS Protection**: Configured for frontend-backend communication├── 

- **Input Validation**: Comprehensive request validation├── 📁 services/              # Business logic

│   ├── 📄 document_service.py # Document processing and search

## 🤝 Contributing│   ├── 🧠 embedding_service.py # Vector embedding generation

│   ├── 💬 chat_service.py     # AI chat with source attribution

1. Fork the repository│   └── 👁️  ocr_service.py     # OCR text extraction

2. Create a feature branch (`git checkout -b feature/amazing-feature`)└── 

3. Commit your changes (`git commit -m 'Add amazing feature'`)└── 📁 uploads/              # Uploaded files storage

4. Push to the branch (`git push origin feature/amazing-feature`)```

5. Open a Pull Request

## 📊 Database Models

## 📝 License

### Document

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.Stores uploaded file information and extracted content.

```sql

---- id (UUID): Unique document identifier

- filename (String): Original filename

**Made with ❤️ by [Harish](https://github.com/harishb2006)**- file_type (String): File extension (pdf, docx, jpg, etc.)
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
