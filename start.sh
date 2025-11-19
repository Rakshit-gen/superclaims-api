#!/bin/bash

echo "SuperClaims Backend - Quick Start Script"
echo "========================================"
echo ""

if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and add your OpenAI API key"
    echo ""
    echo "  cp .env.example .env"
    echo "  nano .env  # Add your API key"
    exit 1
fi


echo "✓ .env file found"
echo ""

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

echo "Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "Interactive docs at: http://localhost:8000/docs"
echo ""

uvicorn main:app --reload
