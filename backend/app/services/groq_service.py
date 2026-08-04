import json
from functools import lru_cache

from groq import Groq

from app.core.config import get_settings
from app.services import paritok_client

settings = get_settings()


@lru_cache
def get_groq_client() -> Groq:
    return Groq(api_key=settings.groq_api_key)


def _chat_json(system_prompt: str, user_prompt: str, model: str, temperature: float = 0.4) -> dict:
    """Call Groq's chat completion with JSON-object mode and return parsed JSON.
    Falls back to a best-effort parse if the model wraps the JSON in prose."""
    client = get_groq_client()
    completion = client.chat.completions.create(
        model=model,
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    raw = completion.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw[start : end + 1])
        raise


def generate_opportunity_dna(profile: dict) -> dict:
    """Phase 1 AI: turn a raw profile into a structured 'Opportunity DNA' summary."""
    system_prompt = (
        "You are an expert career and opportunity-matching analyst. Given a user's "
        "profile, produce a concise, honest analysis. Respond ONLY with a JSON object "
        "with keys: summary (2-3 sentence string), strengths (array of short strings), "
        "weaknesses (array of short strings), career_interests (array of short strings), "
        "personality_summary (1-2 sentence string), recommended_categories (array from "
        "[Scholarships, Jobs, Internships, Grants, Competitions, Accelerators, Fellowships, "
        "Conferences, Events, Volunteering])."
    )
    return _chat_json(system_prompt, json.dumps(profile), settings.groq_reasoning_model)


def rank_and_explain_opportunities(profile: dict, opportunities: list[dict]) -> dict:
    """Phase 4 AI (legacy, non-agentic): given a shortlist of candidate opportunities
    (already narrowed by vector search), pick and rank the top matches with an
    explanation each. Kept as the fallback path for run_recommend_agent()."""
    system_prompt = (
        "You are an AI opportunity-matching engine. You are given a user profile and a "
        "list of candidate opportunities (already pre-filtered by semantic search). "
        "Select and rank the best matches (at most 5, fewer if the pool is small). "
        "Respond ONLY with a JSON object: {\"matches\": [{\"opportunity_id\": string, "
        "\"match_score\": integer 0-100, \"reason\": string (why it fits), "
        "\"missing_skill\": string or null, \"next_step\": string (one concrete action)}]}. "
        "Order matches by match_score descending."
    )
    user_prompt = json.dumps({"profile": profile, "opportunities": opportunities})
    return _chat_json(system_prompt, user_prompt, settings.groq_reasoning_model)


SEARCH_OPPORTUNITIES_TOOL = {
    "type": "function",
    "function": {
        "name": "search_opportunities",
        "description": (
            "Semantic search over the live opportunity knowledge base (scholarships, "
            "jobs, internships, grants, competitions, accelerators, fellowships, "
            "conferences, events, volunteering). Returns candidate opportunities "
            "matching the query, each with an id, title, organization, category, "
            "country, deadline, skills, and a description."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Natural-language search text. Combine what matters most from "
                        "the user's goals, skills, and interests into one query — this "
                        "is what actually drives which opportunities come back."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Max candidates to return.",
                    "default": 20,
                },
            },
            "required": ["query"],
        },
    },
}


def _slim_opportunity(o: dict) -> dict:
    return {
        "id": o["id"],
        "title": o["title"],
        "organization": o.get("organization"),
        "description": (o.get("description") or "")[:500],
        "category": o.get("category"),
        "country": o.get("country"),
        "deadline": o.get("deadline"),
        "skills": o.get("skills"),
    }


def run_recommend_agent(profile: dict, search_fn) -> dict:
    """Agentic matching pipeline: the model itself decides what to search for and
    calls search_opportunities as a real tool — the results come back as an actual
    tool_result message rather than being pre-stuffed into the prompt. This is the
    content type Paritok's compressor is actually trained on (tool results / old
    history), unlike a single static prompt.

    search_fn: Callable[[query: str, limit: int], list[dict]] — the caller (router)
    supplies this since it owns the Supabase client and embedding call; this function
    stays free of DB concerns and just orchestrates the agent loop.

    Returns {"ranked": <parsed JSON from the model's final answer>,
             "candidates_by_id": {id: full opportunity row}}.
    """
    client = get_groq_client()
    model = settings.groq_reasoning_model

    system_prompt = (
        "You are an AI opportunity-matching agent for OpportunityOS. You have a tool, "
        "search_opportunities, that queries a live database of scholarships, jobs, "
        "grants, competitions, and more. Given the user's profile: "
        "1) Call search_opportunities with a query capturing their goals, skills, and "
        "interests. 2) Once you have results, select and rank the best matches (at "
        "most 5, fewer if the pool is small). "
        "Respond with a JSON object: {\"matches\": [{\"opportunity_id\": string, "
        "\"match_score\": integer 0-100, \"reason\": string (why it fits), "
        "\"missing_skill\": string or null, \"next_step\": string}]}, ordered by "
        "match_score descending."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(profile)},
    ]

    # Turn 1 — let the model pick the search query and call the tool.
    first = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=[SEARCH_OPPORTUNITIES_TOOL],
        tool_choice="auto",
        temperature=0.3,
    )
    assistant_msg = first.choices[0].message
    tool_calls = assistant_msg.tool_calls or []

    if not tool_calls:
        # Model answered without searching (shouldn't normally happen with tool_choice
        # nudging it, but stay robust) — fall back to the non-agentic path so a
        # request never just fails.
        fallback_query = " ".join(
            filter(
                None,
                [
                    profile.get("goals", ""),
                    " ".join(profile.get("skills", []) or []),
                    " ".join(profile.get("interests", []) or []),
                ],
            )
        )
        candidates = search_fn(fallback_query or profile.get("education_level", ""), 20)
        candidates_by_id = {c["id"]: c for c in candidates}
        ranked = rank_and_explain_opportunities(profile, [_slim_opportunity(c) for c in candidates])
        return {"ranked": ranked, "candidates_by_id": candidates_by_id}

    messages.append(
        {
            "role": "assistant",
            "content": assistant_msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in tool_calls
            ],
        }
    )

    candidates_by_id: dict = {}
    for tc in tool_calls:
        try:
            args = json.loads(tc.function.arguments or "{}")
        except json.JSONDecodeError:
            args = {}
        query = args.get("query") or profile.get("goals", "") or profile.get("education_level", "")
        limit = args.get("limit", 20)

        results = search_fn(query, limit)
        for r in results:
            candidates_by_id[r["id"]] = r

        # This is the real tool_result message — the content Paritok's compressor
        # actually targets, unlike a plain user-message JSON blob. Compress it via
        # the hosted GPU endpoint before it goes to Groq.
        raw_tool_content = json.dumps([_slim_opportunity(r) for r in results])
        compressed_tool_content = paritok_client.compress(
            raw_tool_content, query=query, kind="tool_result"
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tc.id,
                "content": compressed_tool_content,
            }
        )

    # Turn 2 — model reasons over the tool results now in context and gives the
    # final ranked answer.
    second = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    raw = second.choices[0].message.content
    try:
        ranked = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        ranked = json.loads(raw[start : end + 1]) if start != -1 and end != -1 else {"matches": []}

    return {"ranked": ranked, "candidates_by_id": candidates_by_id}


def generate_roadmap(goal: str, profile: dict | None = None) -> dict:
    """Phase 6 AI: turn a stated goal into a month-by-month roadmap."""
    system_prompt = (
        "You are a career roadmap planner. Given a goal (and optionally a user profile), "
        "produce a realistic month-by-month plan of 3-6 months. Respond ONLY with JSON: "
        "{\"goal\": string, \"summary\": string, \"months\": [{\"month\": integer, "
        "\"title\": string, \"focus_areas\": [string], \"milestones\": [string]}]}."
    )
    user_prompt = json.dumps({"goal": goal, "profile": profile or {}})
    return _chat_json(system_prompt, user_prompt, settings.groq_reasoning_model)


def generate_career_coach_output(profile: dict, opportunity: dict | None = None) -> dict:
    """Phase 5 AI: CV/cover letter/interview prep guidance, optionally targeted at one opportunity."""
    system_prompt = (
        "You are an AI career coach. Given a user profile and optionally a specific "
        "target opportunity, produce actionable prep guidance. Respond ONLY with JSON: "
        "{\"cv_suggestions\": [string], \"cover_letter_draft\": string, "
        "\"portfolio_improvements\": [string], \"skills_to_learn\": [string], "
        "\"interview_tips\": [string], \"timeline\": [string]}."
    )
    user_prompt = json.dumps({"profile": profile, "opportunity": opportunity})
    return _chat_json(system_prompt, user_prompt, settings.groq_reasoning_model)


def generate_cv_document(profile: dict, description: str, opportunity: dict | None = None) -> dict:
    """Generates a structured, ATS-friendly CV using only what the user actually
    provided (skills, education, goals, pasted resume text) — the model is told
    explicitly not to invent employers, titles, or achievements that weren't given."""
    system_prompt = (
        "You are an expert CV writer. Build a professional, honest CV using ONLY "
        "information present in the user's profile (skills, education, goals, "
        "interests, and any pasted resume text). Do NOT invent employers, job "
        "titles, dates, or achievements that are not implied by the given data. "
        "If the user pasted resume text, restructure and polish it. If there is "
        "no work history, build 'experience' entries from real projects/skills/"
        "goals framed honestly (e.g. as coursework, personal projects, or "
        "initiatives) rather than fabricating jobs. Use the user's 'portrayal "
        "note' to choose emphasis and tone, not to add false facts. "
        "Respond ONLY with a JSON object matching this shape: "
        '{"full_name": string, "headline": string (a one-line professional '
        'title/positioning statement), "location": string, "summary": string '
        "(3-4 sentences), \"skills\": [string], \"experience\": "
        '[{"heading": string, "subheading": string, "bullets": [string]}], '
        '"education": [{"heading": string, "subheading": string, "bullets": '
        '[string]}], "languages": [string]}.'
    )
    user_prompt = json.dumps(
        {
            "profile": profile,
            "portrayal_note": description,
            "target_opportunity": opportunity,
        }
    )
    return _chat_json(system_prompt, user_prompt, settings.groq_reasoning_model, temperature=0.5)


def generate_cover_letter_document(profile: dict, description: str, opportunity: dict | None = None) -> dict:
    """Generates a full cover letter (salutation, body paragraphs, closing) —
    distinct from the shorter cover_letter_draft inside the general career-coach
    endpoint, since this one is meant to be exported as a standalone document."""
    system_prompt = (
        "You are an expert cover letter writer. Write a complete, professional "
        "cover letter using ONLY information present in the user's profile. Do "
        "not invent facts. Use the user's 'portrayal note' to guide emphasis and "
        "tone. If a target opportunity is given, address the letter to that role "
        "specifically; otherwise keep it general but still concrete. "
        "Respond ONLY with a JSON object: {\"full_name\": string, "
        '"salutation": string (e.g. "Dear Hiring Manager,"), '
        '"body_paragraphs": [string] (3-4 paragraphs), '
        '"closing": string (e.g. "Sincerely,")}.'
    )
    user_prompt = json.dumps(
        {
            "profile": profile,
            "portrayal_note": description,
            "target_opportunity": opportunity,
        }
    )
    return _chat_json(system_prompt, user_prompt, settings.groq_reasoning_model, temperature=0.5)


def career_chat_reply(profile: dict, history: list[dict], new_message: str, opportunity: dict | None = None) -> str:
    """Multi-turn career chat — follow-up questions on matches, roadmap, or
    CV/cover-letter tone. Unlike the other endpoints (each a fresh single-turn
    call), this genuinely accumulates conversation history across turns and
    resends it every request — the other content type Paritok's compressor
    targets (summarizing/compressing turns beyond a recent window), alongside
    the tool_result content from the /recommend agent.

    history: prior turns as [{"role": "user"|"assistant", "content": str}, ...],
    oldest first. new_message is appended before sending.
    """
    client = get_groq_client()
    system_prompt = (
        "You are an AI career coach chatting with a user about their job/scholarship "
        "search, roadmap, or application materials. Use their profile for context. "
        "Be concise, concrete, and conversational — this is a chat, not a report. "
        "Ask a clarifying question if their request is ambiguous rather than guessing."
    )
    context_note = f"User profile: {json.dumps(profile)}"
    if opportunity:
        context_note += f"\nCurrently discussing this opportunity: {json.dumps(opportunity)}"

    # Once the thread runs long, compress everything except a recent window —
    # this is the "old history" content type Paritok's compressor targets,
    # alongside the tool_result content in the /recommend agent.
    RECENT_WINDOW = 6
    if len(history) > RECENT_WINDOW:
        older, recent = history[:-RECENT_WINDOW], history[-RECENT_WINDOW:]
        older_text = "\n".join(f"{m['role']}: {m['content']}" for m in older)
        compressed_older = paritok_client.compress(
            older_text, query="Summarize prior chat turns for context continuity", kind="tool_result"
        )
        history_for_prompt = [
            {"role": "system", "content": f"Earlier in this conversation:\n{compressed_older}"},
            *recent,
        ]
    else:
        history_for_prompt = history

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": context_note},
        *history_for_prompt,
        {"role": "user", "content": new_message},
    ]

    completion = client.chat.completions.create(
        model=settings.groq_fast_model,
        messages=messages,
        temperature=0.6,
    )
    return completion.choices[0].message.content


def embed_text_fallback_keywords(text: str) -> list[str]:
    """Lightweight keyword extraction used only if a dedicated embedding model isn't
    configured. Real embeddings are produced client-side via the embedding_service."""
    system_prompt = (
        "Extract the 8-15 most important skill/topic keywords from this text. "
        "Respond ONLY with JSON: {\"keywords\": [string]}."
    )
    result = _chat_json(system_prompt, text, settings.groq_fast_model, temperature=0.1)
    return result.get("keywords", [])