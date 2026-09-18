#!/usr/bin/env bash
# Clone the æææ.com repo, set up a clean local environment,
# install dependencies, and verify it runs.

set -euo pipefail

REPO_URL="${1:-https://github.com/yaelm/aeaedotcom.git}"
WORKSPACE="${2:-${HOME}/projects/aeaedotcom}"

cleanup() {
  true
}

main() {
  mkdir -p "$WORKSPACE"
  cd "$WORKSPACE"

  if [ -d aeaedotcom/.git ]; then
    cd aeaedotcom
    echo "Using existing clone in $WORKSPACE/aeaedotcom"
  else
    echo "Cloning æææ.com into $WORKSPACE/aeaedotcom ..."
    git clone "$REPO_URL" aeaedotcom
    cd aeaedotcom
  fi

  echo "Repo root: $(pwd)"
  echo "Branch : $(git branch --show-current)"
  echo "Remote : $(git remote get-url origin 2>/dev/null || echo <no remote>)"
  echo "Last commit: $(git log -1 --oneline)"

  echo "Installing Python deps (quiet, non-interactive)..."
  python -m pip install -q -r requirements.txt

  echo "Python deps installed."
  echo "Python: $(python --version)"
  echo "Pip   : $(python -m pip --version)"

  echo "Starting backend on http://localhost:4174 ..."
  python -m backend.app &
  BACKEND_PID=$!
  sleep 2

  echo "Verifying backend..."
  for path in / /health /api/status /api/brands /api/root /api/receipt /api/manifest; do
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "http://localhost:4174$path" || echo 000)
    echo "GET $path -> $code"
  done

  echo "Stopping backend (pid $BACKEND_PID)..."
  kill $BACKEND_PID || true
  wait $BACKEND_PID || true

  echo "æææ.com local environment is ready."
}

main
