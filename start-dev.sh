#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Smart Financial Coach Development Environment${NC}\n"

# Check if .env file exists
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${RED}❗ Please update backend/.env with your API keys before running the app${NC}\n"
    exit 1
fi

# Start Docker services
echo -e "${GREEN}📦 Starting Docker services...${NC}"
docker-compose up -d postgres redis

# Wait for services to be healthy
echo -e "${GREEN}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Check if Python virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo -e "${GREEN}✓ Python virtual environment found${NC}"
fi

# Activate virtual environment
echo -e "${GREEN}🔧 Activating virtual environment...${NC}"
cd backend
source venv/bin/activate

# Run database migrations
echo -e "${GREEN}📊 Running database migrations...${NC}"
alembic upgrade head

# Start the FastAPI server
echo -e "${GREEN}🎯 Starting FastAPI server...${NC}"
echo -e "${GREEN}API will be available at: http://localhost:8000${NC}"
echo -e "${GREEN}API Documentation: http://localhost:8000/docs${NC}\n"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
