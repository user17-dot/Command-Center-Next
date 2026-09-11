#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR/backend"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install -r requirements.txt

echo ""
echo "XTS Command Center Next"
echo "Dashboard: http://127.0.0.1:8000"
echo "API docs:  http://127.0.0.1:8000/docs"
echo ""

exec .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
