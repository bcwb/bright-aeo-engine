#!/bin/bash
# Azure App Service startup script for Bright AEO Engine.
# Set as the App Service startup command:
#   bash /home/site/wwwroot/startup.sh

set -e

# ── Persistent data directories ───────────────────────────────────────────
# /home/data is on Azure Files (persists across restarts and deployments).
# wwwroot is overwritten on every deploy, so config and results live here.
mkdir -p /home/data/results

# Copy the bundled config to persistent storage on first deploy only.
# Subsequent deployments preserve any changes users made via the UI.
if [ ! -f /home/data/config.json ]; then
    cp /home/site/wwwroot/backend/config.json /home/data/config.json
    echo "Initialised /home/data/config.json from deployment package"
fi

# ── Python dependencies ───────────────────────────────────────────────────
pip install --quiet -r /home/site/wwwroot/backend/requirements.txt

# ── Start the API server ──────────────────────────────────────────────────
# Single worker required: SSE run queues are held in memory, so multiple
# workers would each maintain separate queue state.
cd /home/site/wwwroot
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
