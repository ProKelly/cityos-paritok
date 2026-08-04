"""One-off script: seeds the `opportunities` table with a curated starter dataset
and computes embeddings for each row so semantic search works immediately.

Safe to re-run: skips any entry whose title already exists in the table.
Inserts in small batches — a single request carrying all rows' embedding
vectors (384 floats each) is large enough that Supabase's gateway can reset
the HTTP/2 stream before it completes; chunking avoids that.

Usage (from backend/):
    python -m scripts.seed_opportunities                  # uses seed_data.json
    python -m scripts.seed_opportunities other_file.json  # uses a specific file
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.supabase_client import get_service_client  # noqa: E402
from app.services.embedding_service import embed_texts  # noqa: E402

DEFAULT_DATA_FILE = Path(__file__).parent / "seed_data.json"
BATCH_SIZE = 5


def insert_in_batches(db, rows: list[dict], batch_size: int = BATCH_SIZE):
    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        attempt = 0
        while True:
            attempt += 1
            try:
                res = db.table("opportunities").insert(batch).execute()
                inserted += len(res.data)
                print(f"  batch {i // batch_size + 1}: inserted {len(res.data)} rows")
                break
            except Exception as exc:
                if attempt >= 3:
                    print(f"  batch {i // batch_size + 1}: FAILED after 3 attempts — {exc}")
                    break
                print(f"  batch {i // batch_size + 1}: attempt {attempt} failed ({exc}), retrying...")
                time.sleep(1.5)
    return inserted


def main():
    data_file = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA_FILE
    with open(data_file) as f:
        opportunities = json.load(f)

    print(f"Loaded {len(opportunities)} opportunities from {data_file.name}.")

    db = get_service_client()

    # Dedup by title against what's already in the table, so re-running this
    # script (e.g. after a partial failure, or after adding new entries)
    # doesn't create duplicates.
    existing = db.table("opportunities").select("title").execute()
    existing_titles = {row["title"] for row in (existing.data or [])}
    new_opportunities = [o for o in opportunities if o["title"] not in existing_titles]

    skipped = len(opportunities) - len(new_opportunities)
    if skipped:
        print(f"Skipping {skipped} entr{'y' if skipped == 1 else 'ies'} already in the database.")

    if not new_opportunities:
        print("Nothing new to seed.")
        return

    texts = [
        f"{o['title']}. {o['description']}. Skills: {', '.join(o.get('skills', []))}"
        for o in new_opportunities
    ]
    print(f"Computing embeddings locally (fastembed) for {len(new_opportunities)} new entries...")
    vectors = embed_texts(texts)

    for o, v in zip(new_opportunities, vectors):
        o["embedding"] = v

    print(f"Inserting into Supabase in batches of {BATCH_SIZE}...")
    inserted = insert_in_batches(db, new_opportunities)
    print(f"Inserted {inserted} of {len(new_opportunities)} rows.")


if __name__ == "__main__":
    main()