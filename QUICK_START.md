# 🚀 Knowledge Assistant - Quick Start Guide

Welcome to your **Knowledge Assistant**! This guide will get you up and running in minutes.

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- ✅ **Python 3.11+** installed
- ✅ **Docker and Docker Compose** installed  
- ✅ **Git** installed
- ✅ **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- ✅ **Tesseract OCR** (will be installed automatically)

## 🎯 Option 1: Automated Setup (Recommended)

### Step 1: Run the Setup Script
```bash
./setup.sh
```

This script will:
- Install all system dependencies
- Create Python virtual environment
- Install Python packages
- Setup environment variables
- Start database services
- Create database tables

### Step 2: Add Your API Key
Edit the `.env` file and add your Gemini API key:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 3: Start the Application
```bash
source venv/bin/activate
python main.py
```

## 🛠️ Option 2: Manual Setup

### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv postgresql-client tesseract-ocr docker.io docker-compose
```

**macOS:**
```bash
brew install python@3.11 postgresql tesseract poppler docker docker-compose
```

### Step 2: Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your API keys
nano .env
```

### Step 4: Start Services
```bash
# Start database services
docker-compose up -d postgres redis

# Wait for services to be ready
docker-compose logs postgres
```

### Step 5: Start Application
```bash
# Activate virtual environment
source venv/bin/activate

# Start the backend
python main.py
```

## 🎉 Verify Installation

### 1. Check API Health
Open your browser and go to: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "upload_dir": true
}
```

### 2. Run Test Suite
```bash
python test_system.py
```

This will test:
- Database connection
- File upload functionality
- OCR service
- Gemini AI integration
- Document processing
- Chat functionality

### 3. Access API Documentation
Visit: http://localhost:8000/docs

## 📱 Quick Usage Examples

### Upload Your First Document
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-document.pdf" \
  -F "is_public=false"
```

### Search Your Documents
```bash
curl -X GET "http://localhost:8000/api/documents/search?query=your%20search%20query&k=5"
```

### Chat with Your Documents
```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main topics in my documents?",
    "mode": "chat",
    "max_sources": 5
  }'
```

## 🎨 Frontend Development

To build a frontend interface:

1. **Check the frontend structure guide:**
   ```bash
   cat frontend_structure/README.md
   ```

2. **Create a Next.js frontend:**
   ```bash
   npx create-next-app@latest knowledge-assistant-frontend --typescript --tailwind --app
   ```

3. **Follow the component examples** in the frontend_structure directory

## 🐛 Troubleshooting

### Common Issues

**❌ "Database connection failed"**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

**❌ "Gemini API key not configured"**
- Make sure you've added your API key to `.env` file
- Verify the key is correct at https://makersuite.google.com/app/apikey

**❌ "OCR not working"**
```bash
# Check Tesseract installation
tesseract --version

# Install Tesseract (Ubuntu)
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

**❌ "File upload directory not writable"**
```bash
# Create uploads directory
mkdir -p uploads

# Set permissions
chmod 755 uploads
```

### Get Help

1. **Check the logs:**
   ```bash
   # Application logs
   docker-compose logs backend
   
   # Database logs
   docker-compose logs postgres
   ```

2. **Run the test suite:**
   ```bash
   python test_system.py
   ```

3. **Check service status:**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

## 🌟 What's Next?

### 1. Upload Documents
- Drag and drop files to upload
- Support for PDF, DOCX, images, and text files
- Automatic text extraction and processing

### 2. Start Chatting
- Ask questions about your documents
- Get answers with source citations
- Multiple chat modes: chat, summarize, insights, planning

### 3. Share Documents
- Make documents public
- Generate secure sharing links
- Control access and expiration

### 4. Build Your Frontend
- Use the provided frontend structure
- Create custom interfaces
- Integrate with the API

## 📚 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check system health |
| `/api/documents/upload` | POST | Upload documents |
| `/api/documents/search` | GET | Search documents |
| `/api/chat/` | POST | Chat with AI |
| `/api/public/share` | POST | Create public shares |
| `/docs` | GET | API documentation |

## 🎯 Production Deployment

For production deployment:

```bash
# Use production Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or build production image
docker build -f Dockerfile.prod -t knowledge-assistant .
```

## 🎉 You're Ready!

Your Knowledge Assistant is now running! 

**Access your system at:**
- 🏠 **API Server**: http://localhost:8000
- 📚 **Documentation**: http://localhost:8000/docs  
- ❤️ **Health Check**: http://localhost:8000/health

**Happy knowledge managing!** 🧠✨

---

Need help? Check out the full README.md or create an issue in the repository.