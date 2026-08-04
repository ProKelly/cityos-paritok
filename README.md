# OpportunityOS AI

**Your AI-powered opportunity navigator.** FastAPI backend, Supabase (Postgres + pgvector + Auth), Groq for LLM reasoning — matches users to scholarships, jobs, grants, and competitions, explains why, and generates a roadmap plus CV/cover-letter documents to get there.

[![Built with Paritok](https://img.shields.io/badge/Built%20with-Paritok-1f2d3d)](https://github.com/Paritok-official/paritok-4b-v1)

Built with [Paritok](https://github.com/Paritok-official/paritok-4b-v1) — every Groq call in this app is routed through Paritok's hosted-GPU compression proxy.

---

## Setup

### 1. Supabase

Run `supabase/schema.sql` (and any files under `supabase/migrations/`) in your Supabase project's SQL Editor. Get your project URL, anon key, service role key, and JWT secret from **Project Settings → API**.

### 2. Groq

Get a free API key at [console.groq.com](https://console.groq.com).

### 3. Paritok

Create a free account and API key at [paritok.com](https://paritok.com) → dashboard → API keys. This is what routes our Groq traffic through Paritok's hosted GPU server and makes usage show up on your Paritok dashboard.

### 4. Install and configure

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Supabase, Groq, and Paritok keys
```

### 5. Seed the opportunity knowledge base

```bash
python -m scripts.seed_opportunities
```

### 6. Run it

```bash
bash start.sh
```

This starts the Paritok proxy as a background sidecar (pointed at Groq's OpenAI-compatible endpoint, compressing via Paritok's hosted GPU server), waits for it to be healthy, then starts the FastAPI app on port 8000. API docs at `http://localhost:8000/docs`.

To run without Paritok (e.g. quick local debugging without a Paritok account), set `PARITOK_ENABLED=false` in `.env` and either run `bash start.sh` or `uvicorn app.main:app --reload` directly — the app falls back to calling Groq directly.

---

## How Paritok is integrated

Every LLM call in this app (`app/services/groq_service.py`) goes through the official `groq` Python SDK, which is Stainless-generated and supports a custom `base_url` — same shape as the OpenAI SDK. When `PARITOK_ENABLED=true`, that client is pointed at `http://127.0.0.1:8080` (the local Paritok proxy) instead of Groq's endpoint directly:

```python
# app/services/groq_service.py
if settings.paritok_enabled:
    return Groq(api_key=settings.groq_api_key, base_url=settings.paritok_proxy_url)
```

`start.sh` launches that proxy before the app starts:

```bash
paritok proxy --openai-url https://api.groq.com/openai --port 8080 --config-file paritok.yaml
```

`paritok.yaml` sets `use_gpu_server: true`, so compression runs on Paritok's hosted GPU (not a local model) — the `PARITOK_API_KEY` env var authenticates that and is what makes usage appear on the Paritok dashboard.

Live compression stats are also exposed through our own API at `GET /paritok/stats` (proxies Paritok's own `/stats` endpoint) — useful for a demo screen.

**Where it honestly helps, and where it doesn't:** Paritok's compression model is trained specifically on coding-agent traffic — tool results, file reads, multi-turn history. Most of this app's Groq calls are still single-turn JSON generation with no accumulated context (profile analysis, roadmap, CV/cover-letter generation) — a workload Paritok's own docs describe as one it's *less* suited for. Two endpoints were deliberately restructured to give it real, genuinely compressible traffic instead of chasing the number cosmetically:

- **`POST /recommend`** is now agentic rather than a single static prompt: the model is given a `search_opportunities` **tool** and decides the query itself; we execute the real pgvector search it asks for and return the results as an actual `tool_result` message. That's the exact content type Paritok's 4B model was trained to compress — see `run_recommend_agent()` in `app/services/groq_service.py`.
- **`POST /chat`** (new — a multi-turn "career chat" for follow-up questions on matches, roadmap, or document tone) genuinely accumulates conversation history across turns and resends the full thread every request, rather than each call being stateless. That's the other content type Paritok compresses: history beyond a recent window.

We're reporting Paritok's real numbers from `/paritok/stats` rather than the benchmark's headline 74–95% figures, which come from SWE-bench-style coding-agent sessions and won't match this app's traffic pattern exactly — but these two endpoints are the ones actually built to give the compressor something real to work with, rather than a thin wrapper around a static prompt.

---

## Project structure

```
app/
  core/        config, Supabase client, JWT auth
  models/      Pydantic schemas
  routers/     API endpoints (includes chat.py — the new multi-turn career chat)
  services/    Groq (LLM) and embedding logic (run_recommend_agent, career_chat_reply)
scripts/       seed_opportunities.py — loads the curated starter dataset
supabase/      schema.sql + migrations/ (003_career_chat.sql adds chat tables)
career-chat.vue  frontend page for the new /chat endpoint — drop into frontend/pages/
start.sh       launches the Paritok proxy sidecar, then the app
paritok.yaml   Paritok proxy config (hosted GPU server)
```
