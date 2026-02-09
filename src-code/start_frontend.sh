#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🎨 Starting Frontend...${NC}"
echo ""

# Gehe zum Frontend-Ordner
cd "$(dirname "$0")/frontend"

# Prüfe ob node_modules existiert
if [ ! -d "node_modules" ]; then
    echo "�� Installing npm packages..."
    npm install
fi

# Starte Frontend
echo -e "${GREEN}✓ Starting React development server...${NC}"
echo ""
echo -e "${BLUE}Frontend läuft auf:${NC}"
echo "  🌐 http://localhost:3000"
echo ""
echo "Drücke Ctrl+C zum Stoppen"
echo ""

npm start
