"""Calls Paritok's hosted GPU compression endpoint directly, per-request —
no local proxy process, no CLI, no Ollama. Point of this over the proxy setup:
one HTTP call per compressible payload instead of a sidecar process to manage.

Every call is wrapped so a network hiccup, auth error, or unexpected response
shape degrades to "use the original content" rather than breaking the request
that content was for — compression is an optimization, never a hard dependency.
"""

import httpx

from app.core.config import get_settings

settings = get_settings()

COMPRESS_URL = "https://www.paritok.com/api/compress"

# Running totals for our own /paritok/stats endpoint (no local proxy /stats to
# proxy through anymore — we track this ourselves).
_stats = {"calls": 0, "errors": 0, "original_chars": 0, "compressed_chars": 0}


def get_local_stats() -> dict:
    saved = _stats["original_chars"] - _stats["compressed_chars"]
    ratio = (saved / _stats["original_chars"]) if _stats["original_chars"] else 0.0
    return {
        "calls": _stats["calls"],
        "errors": _stats["errors"],
        "original_chars": _stats["original_chars"],
        "compressed_chars": _stats["compressed_chars"],
        "chars_saved": saved,
        "approx_ratio_saved": round(ratio, 4),
        "note": "Character counts, not tokens — a rough proxy since we don't "
        "tokenize client-side. Cross-check exact figures on the Paritok dashboard.",
    }


def compress(content: str, query: str, kind: str = "tool_result") -> str:
    """Compress `content` via Paritok's hosted GPU endpoint. `query` should
    describe what the content will be used for (helps the compressor keep
    what's relevant). `kind` classifies the content type — "tool_result" is
    the one we've confirmed matches Paritok's own vocabulary; other values
    are best-effort and will just no-op (fall back to original) if rejected.

    Returns the compressed string, or the original `content` unchanged if
    Paritok isn't enabled/configured or the call fails for any reason.
    """
    if not settings.paritok_enabled or not settings.paritok_api_key:
        return content

    _stats["calls"] += 1
    _stats["original_chars"] += len(content)

    try:
        resp = httpx.post(
            COMPRESS_URL,
            headers={
                "Authorization": f"Bearer {settings.paritok_api_key}",
                "Content-Type": "application/json",
            },
            json={"content": content, "query": query, "kind": kind},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        compressed = data.get("compressed")
        if not compressed or not isinstance(compressed, str):
            _stats["compressed_chars"] += len(content)
            return content
        _stats["compressed_chars"] += len(compressed)
        return compressed
    except Exception:
        _stats["errors"] += 1
        _stats["compressed_chars"] += len(content)  # no savings counted on a failed call
        return content
