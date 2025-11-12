#!/bin/bash

# Cameroon Traffic App - Quick Setup Script
# This script helps set up the development environment

set -e  # Exit on error

echo "🚗 Cameroon Traffic App - Development Setup"
echo "==========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print success message
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Print error message
error() {
    echo -e "${RED}✗${NC} $1"
}

# Print warning message
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    success "Node.js installed: $NODE_VERSION"
else
    error "Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    success "Python installed: $PYTHON_VERSION"
elif command_exists python; then
    PYTHON_VERSION=$(python --version)
    success "Python installed: $PYTHON_VERSION"
else
    error "Python not found. Please install Python 3.11+ from https://python.org/"
    exit 1
fi

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    success "Docker installed: $DOCKER_VERSION"
else
    warning "Docker not found. Install Docker Desktop from https://docker.com/"
fi

# Check Docker Compose
if command_exists docker-compose; then
    COMPOSE_VERSION=$(docker-compose --version)
    success "Docker Compose installed: $COMPOSE_VERSION"
else
    warning "Docker Compose not found. It's included with Docker Desktop."
fi

# Check Git
if command_exists git; then
    GIT_VERSION=$(git --version)
    success "Git installed: $GIT_VERSION"
else
    error "Git not found. Please install Git from https://git-scm.com/"
    exit 1
fi

echo ""
echo "Setting up project..."
echo ""

# Backend setup
echo "📦 Setting up backend..."

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv || python -m venv venv
    success "Virtual environment created"
else
    success "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || {
    warning "Could not activate virtual environment automatically"
    echo "Please activate it manually:"
    echo "  On macOS/Linux: source venv/bin/activate"
    echo "  On Windows: venv\\Scripts\\activate"
}

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
success "Python dependencies installed"

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    success ".env file created - Please edit it with your configuration"
else
    success ".env file already exists"
fi

cd ..

# Mobile setup
echo ""
echo "📱 Setting up mobile app..."

cd mobile

# Install Node dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies (this may take a few minutes)..."
    npm install
    success "Node.js dependencies installed"
else
    success "Node.js dependencies already installed"
fi

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    success ".env file created - Please edit it with your configuration"
else
    success ".env file already exists"
fi

cd ..

# Docker setup
echo ""
echo "🐳 Setting up Docker services..."

if command_exists docker-compose; then
    echo "Starting PostgreSQL and Redis..."
    docker-compose up -d postgres redis
    
    # Wait for services to be healthy
    echo "Waiting for services to be ready..."
    sleep 5
    
    if docker-compose ps | grep -q "Up"; then
        success "Docker services started"
    else
        warning "Docker services may not have started correctly"
        echo "Run 'docker-compose ps' to check status"
    fi
else
    warning "Docker Compose not available. Skipping Docker setup."
    echo "You can start services later with: docker-compose up -d"
fi

# Git setup
echo ""
echo "📝 Git repository setup..."

if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    success "Git repository initialized"
    
    echo "Do you want to create an initial commit? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "feat: initial project setup with documentation and structure"
        success "Initial commit created"
    fi
else
    success "Git repository already initialized"
fi

# Summary
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure environment variables:"
echo "   - Edit backend/.env with your settings"
echo "   - Edit mobile/.env with your API keys"
echo ""
echo "2. Set up third-party services:"
echo "   - Create Firebase project"
echo "   - Get Mapbox access token"
echo "   - (Optional) Set up Sentry"
echo ""
echo "3. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Test the API:"
echo "   curl http://localhost:8000/api/v1/health"
echo "   Open http://localhost:8000/api/docs in browser"
echo ""
echo "5. Read the documentation:"
echo "   - PROJECT_DOCUMENTATION.md - Complete technical docs"
echo "   - PROGRESS.md - Development progress tracker"
echo "   - docs/guides/SETUP.md - Detailed setup guide"
echo ""
echo "For help, see: docs/guides/SETUP.md"
echo ""
echo "Happy coding! 🚀"

