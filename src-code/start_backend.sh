#!/bin/bash

# Farben für schöne Ausgabe
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Emergency Call System Backend...${NC}"
echo ""

# Gehe zum Projekt-Ordner
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Aktiviere venv automatisch
echo -e "${GREEN}✓ Activating virtual environment...${NC}"
source venv/bin/activate

# Prüfe ob .env existiert
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env template..."
    cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
AI_MODEL=gpt-4o-mini
AI_TEMPERATURE=0.3
EOF
    echo "Please edit .env and add your OpenAI API key!"
    exit 1
fi

# Prüfe ob requirements installiert sind
echo -e "${GREEN}✓ Checking dependencies...${NC}"
pip list | grep -q fastapi || {
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
}

# Starte Server
echo -e "${GREEN}✓ Starting FastAPI server...${NC}"
echo ""
echo -e "${BLUE}Backend läuft auf:${NC}"
echo "  📡 API:  http://localhost:8000"
echo "  📚 Docs: http://localhost:8000/docs"
echo ""
echo "Drücke Ctrl+C zum Stoppen"
echo ""

python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
