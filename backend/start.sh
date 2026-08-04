#!/usr/bin/env bash
# Starts the Paritok proxy (compresses requests, forwards to Groq) as a
# background sidecar, then starts the FastAPI app in the foreground.
# Both run in the same container so the app can reach the proxy at
# 127.0.0.1 — this matters on PaaS platforms where separate Procfile
# process types run on separate machines and can't share localhost.
set -euo pipefail

# Local dev convenience: load .env if present and not already loaded by the
# platform's own env injection (deployed platforms set these directly).
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

PARITOK_ENABLED="${PARITOK_ENABLED:-true}"

if [ "$PARITOK_ENABLED" = "true" ] || [ "$PARITOK_ENABLED" = "True" ]; then
  echo "[start.sh] Starting Paritok proxy (Groq upstream, hosted GPU compression)..."
  paritok proxy \
    --openai-url https://api.groq.com/openai \
    --port 8080 \
    --config-file paritok.yaml &
  PARITOK_PID=$!

  echo "[start.sh] Waiting for Paritok proxy to become healthy..."
  for i in $(seq 1 30); do
    if curl -sf http://127.0.0.1:8080/health > /dev/null 2>&1; then
      echo "[start.sh] Paritok proxy is up (pid $PARITOK_PID)."
      break
    fi
    if [ "$i" -eq 30 ]; then
      echo "[start.sh] WARNING: Paritok proxy did not become healthy in time — continuing anyway."
      echo "[start.sh] The proxy warns rather than aborts on backend issues, so Groq calls may still work once it recovers."
    fi
    sleep 1
  done
else
  echo "[start.sh] PARITOK_ENABLED=false — skipping proxy, app will call Groq directly."
fi

echo "[start.sh] Starting FastAPI app..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
