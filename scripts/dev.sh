#!/usr/bin/env bash
# skywatch development startup script
#
# Starts both the FastAPI backend and Next.js frontend in parallel.
# Requires: Python 3.11+, Node.js 20+, pip, npm
#
# Usage: ./scripts/dev.sh
#

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$REPO_ROOT/services/api"
WEB_DIR="$REPO_ROOT/apps/web"

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║         skywatch dev server           ║"
echo "  ║  Privacy-first AI weather prototype   ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"

# ── Check for .env ────────────────────────────────────────────────────────────
if [ ! -f "$REPO_ROOT/.env" ]; then
    echo -e "${YELLOW}⚠  .env not found — copying from .env.example${NC}"
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    echo -e "${GREEN}✓  Created .env (all keys optional — app works without them)${NC}"
fi

# ── Install Python deps ───────────────────────────────────────────────────────
echo -e "\n${CYAN}[API] Installing Python dependencies...${NC}"
cd "$API_DIR"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --quiet -r requirements.txt
echo -e "${GREEN}[API] Dependencies installed${NC}"

# ── Install Node deps ─────────────────────────────────────────────────────────
echo -e "\n${CYAN}[WEB] Installing Node.js dependencies...${NC}"
cd "$WEB_DIR"
npm install --silent
echo -e "${GREEN}[WEB] Dependencies installed${NC}"

# ── Start services ────────────────────────────────────────────────────────────
echo -e "\n${GREEN}Starting services...${NC}"
echo -e "  API: http://localhost:8000 (FastAPI)"
echo -e "  WEB: http://localhost:3000 (Next.js)"
echo -e "  Docs: http://localhost:8000/docs (Swagger UI)"
echo -e "\n${YELLOW}Press Ctrl+C to stop both services${NC}\n"

# Start FastAPI in background
cd "$API_DIR"
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

# Small delay to let the API start before the frontend
sleep 2

# Start Next.js in background
cd "$WEB_DIR"
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev &
WEB_PID=$!

echo -e "${GREEN}✓ skywatch is running!${NC}"
echo -e "  Open http://localhost:3000 in your browser\n"

# ── Cleanup on exit ───────────────────────────────────────────────────────────
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    kill $API_PID 2>/dev/null || true
    kill $WEB_PID 2>/dev/null || true
    wait $API_PID $WEB_PID 2>/dev/null || true
    echo -e "${GREEN}All services stopped.${NC}"
}

trap cleanup INT TERM EXIT

# Wait for both processes
wait $API_PID $WEB_PID
