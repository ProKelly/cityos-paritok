"""Local text embeddings via fastembed (ONNX runtime, no GPU/torch required).

We use BAAI/bge-small-en-v1.5 (384 dimensions) so it matches the `vector(384)`
columns defined in the Supabase schema (see backend/supabase/schema.sql).
Groq is used for reasoning/generation; embeddings are kept local since Groq
does not expose an embeddings endpoint.
"""

from functools import lru_cache

from fastembed import TextEmbedding

MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384


@lru_cache
def get_embedding_model() -> TextEmbedding:
    return TextEmbedding(model_name=MODEL_NAME)


def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    vector = next(model.embed([text]))
    return vector.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    return [v.tolist() for v in model.embed(texts)]
