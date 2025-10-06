#!/bin/bash

# Knowledge Assistant Startup Script
# This script starts both the backend and frontend servers

echo "🚀 Starting Knowledge Assistant..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Start backend server
echo "📡 Starting backend server..."
source venv/bin/activate
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Start frontend server
echo "🌐 Starting frontend server..."
cd frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

cd ..

echo "✅ Knowledge Assistant is running!"
echo "📖 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:5177 (port may vary)"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📋 To stop the servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📄 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"