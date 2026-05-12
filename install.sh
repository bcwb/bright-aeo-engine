#!/usr/bin/env bash
# Bright AEO Engine — install script
# Run once after cloning: bash install.sh

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

info()    { echo -e "${BOLD}$*${RESET}"; }
success() { echo -e "${GREEN}✓ $*${RESET}"; }
warn()    { echo -e "${YELLOW}⚠ $*${RESET}"; }
error()   { echo -e "${RED}✗ $*${RESET}"; exit 1; }

echo ""
echo -e "${BOLD}Bright AEO Engine — Setup${RESET}"
echo "──────────────────────────────────────"

# ── Check prerequisites ──────────────────────────────────────────────────────

info "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
  error "Python 3 is not installed. Install it from https://www.python.org/downloads/ and re-run."
fi
PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
success "Python $PY_VERSION found"

if ! command -v node &>/dev/null; then
  error "Node.js is not installed. Install it from https://nodejs.org/ and re-run."
fi
NODE_VERSION=$(node --version)
success "Node.js $NODE_VERSION found"

if ! command -v npm &>/dev/null; then
  error "npm is not installed (should come with Node.js). Re-install Node.js and re-run."
fi

# ── Python virtual environment ───────────────────────────────────────────────

info ""
info "Setting up Python virtual environment..."

cd backend

if [ ! -d "venv" ]; then
  python3 -m venv venv
  success "Created venv"
else
  success "venv already exists, skipping creation"
fi

source venv/bin/activate
success "Activated venv"

info "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
success "Python dependencies installed"

deactivate
cd ..

# ── Node / npm dependencies ──────────────────────────────────────────────────

info ""
info "Installing frontend dependencies..."

cd frontend
npm install --silent
success "Node dependencies installed"
cd ..

# ── Environment file ─────────────────────────────────────────────────────────

info ""
info "Checking environment configuration..."

if [ ! -f ".env" ]; then
  cp .env.example .env
  warn ".env created from .env.example — IMPORTANT: open .env and fill in your API keys before running the app."
else
  success ".env already exists"
fi

# ── gstack (Claude Code skills) ──────────────────────────────────────────────

info ""
info "Setting up gstack Claude Code skills..."

if [ -d "$HOME/.claude/skills/gstack" ]; then
  success "gstack already installed at ~/.claude/skills/gstack"
elif command -v git &>/dev/null && command -v bun &>/dev/null; then
  git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git "$HOME/.claude/skills/gstack" \
    && cd "$HOME/.claude/skills/gstack" && ./setup && cd - > /dev/null
  success "gstack installed"
else
  warn "gstack skipped — requires git and bun. Install bun (https://bun.sh) then run: git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup"
fi

# ── Done ─────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}──────────────────────────────────────${RESET}"
echo -e "${GREEN}${BOLD}Setup complete!${RESET}"
echo ""
echo -e "Next steps:"
echo -e "  1. Edit ${BOLD}.env${RESET} and add your API keys (Anthropic, OpenAI, Google, Perplexity)"
echo ""
echo -e "To start the app, open two terminals:"
echo ""
echo -e "  ${BOLD}Terminal 1 — Backend:${RESET}"
echo -e "    cd backend"
echo -e "    source venv/bin/activate"
echo -e "    uvicorn main:app --reload --port 8000"
echo ""
echo -e "  ${BOLD}Terminal 2 — Frontend:${RESET}"
echo -e "    cd frontend"
echo -e "    npm run dev"
echo ""
echo -e "Then open ${BOLD}http://localhost:5173${RESET} in your browser."
echo ""
