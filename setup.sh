#!/bin/bash

# Knowledge Assistant Setup Script
# This script sets up the complete Knowledge Assistant project

set -e  # Exit on any error

echo "🧠 Knowledge Assistant Setup"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    print_status "Checking operating system..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_success "Linux detected"
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_success "macOS detected"
        OS="macos"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check and install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if [[ "$OS" == "linux" ]]; then
        # Update package list
        sudo apt-get update
        
        # Install required packages
        sudo apt-get install -y \
            python3 \
            python3-pip \
            python3-venv \
            postgresql-client \
            tesseract-ocr \
            tesseract-ocr-eng \
            poppler-utils \
            docker.io \
            docker-compose \
            curl \
            git
            
    elif [[ "$OS" == "macos" ]]; then
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            print_error "Homebrew is not installed. Please install it first: https://brew.sh/"
            exit 1
        fi
        
        # Install required packages
        brew install \
            python@3.11 \
            postgresql \
            tesseract \
            poppler \
            docker \
            docker-compose
    fi
    
    print_success "System dependencies installed"
}

# Create Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    pip install -r requirements.txt
    
    print_success "Python environment configured"
}

# Setup environment variables
setup_env() {
    print_status "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Created .env file from .env.example"
        print_warning "Please edit .env file and add your GEMINI_API_KEY"
        
        # Prompt for Gemini API key
        echo
        echo "To get a Gemini API key:"
        echo "1. Go to https://makersuite.google.com/app/apikey"
        echo "2. Create a new API key"
        echo "3. Copy the key and paste it below"
        echo
        read -p "Enter your Gemini API key (or press Enter to skip): " gemini_key
        
        if [ ! -z "$gemini_key" ]; then
            sed -i "s/your_gemini_api_key_here/$gemini_key/" .env
            print_success "Gemini API key configured"
        else
            print_warning "You'll need to manually add your Gemini API key to .env file"
        fi
    else
        print_success ".env file already exists"
    fi
    
    # Create uploads directory
    mkdir -p uploads
    print_success "Uploads directory created"
}

# Start database and services
start_services() {
    print_status "Starting database and services..."
    
    # Start Docker services
    docker-compose up -d postgres redis
    
    # Wait for PostgreSQL to be ready
    print_status "Waiting for PostgreSQL to be ready..."
    until docker-compose exec postgres pg_isready -U postgres; do
        sleep 2
    done
    
    print_success "Database services started"
}

# Run database migrations
setup_database() {
    print_status "Setting up database..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run the application briefly to create tables
    print_status "Creating database tables..."
    timeout 10s python main.py || true
    
    print_success "Database setup completed"
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check if services are running
    if ! docker-compose ps | grep "Up" > /dev/null; then
        print_error "Docker services are not running properly"
        return 1
    fi
    
    # Test database connection
    if ! docker-compose exec postgres psql -U postgres -d knowledge_assistant -c "SELECT 1;" > /dev/null 2>&1; then
        print_error "Cannot connect to database"
        return 1
    fi
    
    print_success "Installation verified successfully"
}

# Print next steps
print_next_steps() {
    echo
    echo "🎉 Knowledge Assistant setup complete!"
    echo
    echo "Next steps:"
    echo "1. Make sure your Gemini API key is set in .env file"
    echo "2. Start the backend server:"
    echo "   source venv/bin/activate"
    echo "   python main.py"
    echo
    echo "3. The API will be available at: http://localhost:8000"
    echo "4. API documentation: http://localhost:8000/docs"
    echo
    echo "For frontend setup, see the frontend directory"
    echo
    echo "Useful commands:"
    echo "- View logs: docker-compose logs"
    echo "- Stop services: docker-compose down"
    echo "- Restart services: docker-compose restart"
    echo
}

# Main setup flow
main() {
    echo "Starting Knowledge Assistant setup..."
    echo
    
    check_os
    install_system_deps
    setup_python_env
    setup_env
    start_services
    setup_database
    verify_installation
    print_next_steps
    
    print_success "Setup completed successfully! 🚀"
}

# Run main function
main "$@"