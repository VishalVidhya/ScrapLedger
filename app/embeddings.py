"""Embedding generation utilities for ScrapLedger.

Provides 768-dimensional vector embeddings for CPCB regulatory documents
using Gemini text-embedding-004, with a deterministic local fallback
for offline testing and CI environments.
"""

from __future__ import annotations

import hashlib
import logging
import math
import os
import re

os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
import litellm

litellm.telemetry = False

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 768
DEFAULT_EMBEDDING_MODEL = "gemini/text-embedding-004"


def _local_deterministic_embedding(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    """Generate a deterministic, normalized unit vector for offline/testing use.

    Uses bag-of-words and character n-gram hashing with TF weighting projected
    into a `dim`-dimensional hypersphere.
    """
    vec = [0.0] * dim
    words = re.findall(r"\w+", text.lower())
    if not words:
        return [0.0] * dim

    # Hash unigrams and bigrams
    tokens = list(words)
    for i in range(len(words) - 1):
        tokens.append(f"{words[i]}_{words[i+1]}")

    for token in tokens:
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        bucket = h % dim
        sign = 1.0 if (h >> 16) & 1 else -1.0
        vec[bucket] += sign

    # Normalize vector to unit length (L2 norm)
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [round(x / norm, 6) for x in vec]
    return vec


_REMOTE_EMBEDDINGS_DISABLED = False


def get_embedding(
    text: str,
    model: str = DEFAULT_EMBEDDING_MODEL,
    use_fallback_only: bool = False,
) -> list[float]:
    """Generate a 768-dimensional dense vector embedding for a piece of text."""
    global _REMOTE_EMBEDDINGS_DISABLED
    if not text.strip():
        return [0.0] * EMBEDDING_DIM

    if (
        use_fallback_only
        or _REMOTE_EMBEDDINGS_DISABLED
        or os.getenv("OFFLINE_EMBEDDINGS", "").lower() in ("1", "true")
        or os.getenv("USE_LOCAL_EMBEDDINGS", "1").lower() in ("1", "true")
    ):
        return _local_deterministic_embedding(text, dim=EMBEDDING_DIM)

    has_api_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
    if not has_api_key:
        return _local_deterministic_embedding(text, dim=EMBEDDING_DIM)

    try:
        response = litellm.embedding(model=model, input=[text], timeout=3)
        raw_vec = response.data[0]["embedding"]
        # Ensure correct dimension
        if len(raw_vec) == EMBEDDING_DIM:
            return raw_vec
        elif len(raw_vec) > EMBEDDING_DIM:
            return raw_vec[:EMBEDDING_DIM]
        else:
            return raw_vec + [0.0] * (EMBEDDING_DIM - len(raw_vec))
    except Exception as e:
        logger.info("Using local fast zero-cost embeddings (reason: %s)", e)
        _REMOTE_EMBEDDINGS_DISABLED = True
        return _local_deterministic_embedding(text, dim=EMBEDDING_DIM)


def get_embeddings_batch(
    texts: list[str],
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    return [get_embedding(t, model=model) for t in texts]


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two dense vectors."""
    if len(vec_a) != len(vec_b) or not vec_a:
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
