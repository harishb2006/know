#!/bin/bash

# Knowledge Assistant Setup Script
# This script sets up the development environment

echo "🛠️  Setting up Knowledge Assistant..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup frontend
echo "🌐 Setting up frontend..."
cd frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js and npm first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ NPM version: $(npm --version)"

# Install frontend dependencies
echo "📚 Installing frontend dependencies..."
npm install

cd ..

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p chroma_db

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your API keys and credentials"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your credentials:"
echo "   - GEMINI_API_KEY"
echo "   - MONGO_URI"
echo "   - JWT_SECRET_KEY"
echo ""
echo "2. Start the application:"
echo "   ./scripts/start.sh"
echo ""
echo "3. Open your browser:"
echo "   http://localhost:5177"