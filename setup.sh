#!/bin/bash

# Distributed LLM Serving - Setup Script
# for Windows WSL2 Environment

set -e  # Exit immediately if a command fails

echo "Starting Distributed LLM Serving setup..."

# check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

# check Docker
echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "   Docker not found. Please install Docker Desktop."
    exit 1
fi
echo "   Docker is installed"

# create project directories
echo "Creating project directories..."
mkdir -p app/routers
mkdir -p engine
mkdir -p middleware
mkdir -p tests
mkdir -p monitoring/grafana/dashboards

# create __init__.py files
echo "📝 Creating __init__.py files..."
touch app/__init__.py
touch app/routers/__init__.py
touch engine/__init__.py
touch middleware/__init__.py
touch tests/__init__.py

# create .env file from example
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Created .env (you can edit it later)"
else
    echo ".env already exists, skipping"
fi

# create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "venv already exists, skipping"
fi

# activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start the server (local):"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. OR start with Docker:"
echo "   docker-compose up --build"
echo ""
echo "4. Access the API:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - Metrics: http://localhost:8000/metrics"
echo "   - Grafana: http://localhost:3000 (if using Docker)"
echo ""
echo "5. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "See README.md for more details"
echo ""