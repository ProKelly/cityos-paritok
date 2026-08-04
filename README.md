# OpportunityOS AI

**Your AI-powered opportunity navigator.** FastAPI backend, Supabase (Postgres + pgvector + Auth), Groq for LLM reasoning — matches users to scholarships, jobs, grants, and competitions, explains why, and generates a roadmap plus CV/cover-letter documents to get there.

[![Built with Paritok](https://img.shields.io/badge/Built%20with-Paritok-1f2d3d)](https://github.com/Paritok-official/paritok-4b-v1)

Built with [Paritok](https://github.com/Paritok-official/paritok-4b-v1) — the two endpoints in this app with real compressible content (`/recommend`'s tool results, `/chat`'s conversation history) route through Paritok's hosted GPU compression endpoint before hitting Groq.

---

## Setup

### 1. Supabase

Run `supabase/schema.sql` (and everything under `supabase/migrations/`) in your Supabase project's SQL Editor. Get your project URL, anon key, service role key, and JWT secret from **Project Settings → API**.

### 2. Groq

Get a free API key at [console.groq.com](https://console.groq.com).

### 3. Paritok

Create a free account and API key at [paritok.com](https://paritok.com) → dashboard → API keys. No install beyond that — this app calls Paritok's hosted GPU endpoint directly over HTTP, no local proxy process or CLI needed.

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
uvicorn app.main:app --reload --port 8000
```

That's it — one process. API docs at `http://localhost:8000/docs`.

To run without Paritok (e.g. no API key yet), set `PARITOK_ENABLED=false` in `.env` — the app calls Groq directly and skips compression entirely.

---

## How Paritok is integrated

Rather than wrapping every Groq call in a proxy, this app calls Paritok's **hosted GPU compress endpoint** (`app/services/paritok_client.py`) directly, only where there's genuinely compressible content:

```python
# app/services/paritok_client.py
resp = httpx.post(
    "https://www.paritok.com/api/compress",
    headers={"Authorization": f"Bearer {settings.paritok_api_key}"},
    json={"content": content, "query": query, "kind": kind},
)
```

**Where it honestly helps, and where it doesn't:** Paritok's compression model is trained specifically on coding-agent traffic — tool results, file reads, multi-turn history. Most of this app's Groq calls are single-turn JSON generation with no accumulated context (profile analysis, roadmap, CV/cover-letter generation) — a workload Paritok's own docs describe as one it's *less* suited for. Two endpoints were deliberately restructured to give it real, genuinely compressible traffic instead of chasing the number cosmetically:

- **`POST /recommend`** is agentic rather than a single static prompt: the model is given a `search_opportunities` **tool** and decides the query itself; we execute the real pgvector search it asks for, compress the results through Paritok, and return them as an actual `tool_result` message — see `run_recommend_agent()` in `app/services/groq_service.py`.
- **`POST /chat`** (a multi-turn "career chat" for follow-up questions on matches, roadmap, or document tone) genuinely accumulates conversation history across turns. Once a thread passes 6 turns, everything older than the most recent 6 is compressed through Paritok before being resent — see `career_chat_reply()`.

Every `compress()` call fails safe: if Paritok is unreachable, misconfigured, or returns something unexpected, the original uncompressed content is used and the request still succeeds — compression is an optimization here, never a hard dependency.

Running totals (calls made, characters in vs. out) are exposed at `GET /paritok/stats` for a demo screen — character-based since we don't tokenize client-side; cross-check exact token/cost figures on the Paritok dashboard itself, which tracks by API key server-side.

We're reporting these real numbers rather than the benchmark's headline 74–95% figures, which come from SWE-bench-style coding-agent sessions with much heavier tool-output repetition than a single search call or a short chat thread — a smaller, honest number here is more credible than an inflated one that doesn't match the dashboard.

---

## Project structure

```
app/
  core/        config, Supabase client, JWT auth
  models/      Pydantic schemas
  routers/     API endpoints (chat.py — multi-turn career chat; paritok.py — /paritok/stats)
  services/
    groq_service.py     LLM calls (run_recommend_agent, career_chat_reply, etc.)
    paritok_client.py   direct HTTP client for Paritok's hosted compress endpoint
    embedding_service.py
scripts/       seed_opportunities.py — loads the curated starter dataset
supabase/      schema.sql + migrations/ (003_career_chat.sql adds chat tables)
career-chat.vue  frontend page for /chat — drop into frontend/pages/
```