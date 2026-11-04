import json
import logging
import os
from contextlib import asynccontextmanager

# Use local cost map and disable telemetry to prevent network blocking on startup
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"

from typing import Annotated, Any  # noqa: E402

import litellm  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from fastapi import Depends, FastAPI, HTTPException  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402
from litellm import completion, completion_cost  # noqa: E402

from app.config import Settings, get_settings  # noqa: E402
from app.db import init_db, load_chunks_from_cache, search_chunks  # noqa: E402
from app.embeddings import get_embedding  # noqa: E402
from app.schemas import (  # noqa: E402
    AskRequest,
    AskResponse,
    ChatRequest,
    Citation,
    HealthResponse,
    UsageResponse,
)

load_dotenv()
litellm.telemetry = False
litellm.drop_params = True

logger = logging.getLogger("scrapledger")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema if available and warm up vector cache
    init_db()
    cache_path = os.getenv("CHUNKS_CACHE_PATH", "data/chunks_store.json")
    loaded = load_chunks_from_cache(cache_path)
    logger.info("Warmed up vector store with %d cached regulatory chunks.", loaded)
    yield


app = FastAPI(
    title="ScrapLedger API",
    description="Compliance and EPR Analyst Assistant for CPCB regulations",
    version="0.3.0",
    lifespan=lifespan,
)

# In-memory database for tracking real API usage and costs
token_usage_db: dict[str, Any] = {
    "total_tokens": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "cost_usd": 0.0,
    "total_calls": 0,
}

FALLBACK_MODELS = [
    "gemini/gemini-flash-latest",
    "gemini/gemini-1.5-flash",
    "gemini/gemini-pro-latest",
    "gpt-4o-mini",
    "claude-3-haiku-20240307",
]


@app.get("/health", response_model=HealthResponse)
def health_check(settings: Annotated[Settings, Depends(get_settings)]):
    """Health check endpoint for Docker and CI/CD."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/usage", response_model=UsageResponse)
def get_usage():
    """Returns actual LLM token usage and accumulated cost."""
    return token_usage_db


@app.post("/chat")
def chat_with_agent(
    request: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
):
    """
    Calls an LLM to answer compliance queries and returns structured JSON or streams tokens.
    Includes timeouts, retries, and a multi-provider fallback model chain.
    """
    models = [request.model] if request.model else []
    for model in [settings.primary_model] + FALLBACK_MODELS:
        if model not in models:
            models.append(model)

    messages = [
        {
            "role": "system",
            "content": (
                "You are ScrapLedger, a regulatory compliance assistant for CPCB e-waste "
                "and battery waste rules. Always return answers in clear, structured JSON format."
            ),
        },
        {"role": "user", "content": request.query},
    ]

    # Handle streaming response
    if request.stream:
        for model in models:
            try:
                stream_resp = completion(
                    model=model,
                    messages=messages,
                    stream=True,
                    timeout=settings.llm_timeout,
                    num_retries=settings.llm_retries,
                )

                def event_stream(resp=stream_resp):
                    for chunk in resp:
                        delta = chunk.choices[0].delta.content or ""
                        if delta:
                            yield f"data: {json.dumps({'content': delta})}\n\n"
                    yield "data: [DONE]\n\n"

                return StreamingResponse(event_stream(), media_type="text/event-stream")
            except Exception as e:
                logger.warning(f"Streaming model {model} failed: {e}. Trying fallback...")
                continue
        raise HTTPException(status_code=503, detail="All AI models are currently unavailable.")

    # Handle standard structured JSON response
    for model in models:
        try:
            extra_kwargs: dict[str, Any] = {}
            if "gemini" in model:
                gemini_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
                if gemini_key:
                    extra_kwargs["api_key"] = gemini_key

            response = completion(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                timeout=settings.llm_timeout,
                num_retries=settings.llm_retries,
                **extra_kwargs,
            )

            prompt_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
            completion_tokens = getattr(response.usage, "completion_tokens", 0) or 0
            total_tokens = getattr(
                response.usage, "total_tokens", prompt_tokens + completion_tokens
            ) or 0

            try:
                cost = completion_cost(completion_response=response) or 0.0
            except Exception:
                cost = 0.0

            # Update global usage accumulator
            token_usage_db["total_tokens"] += total_tokens
            token_usage_db["prompt_tokens"] += prompt_tokens
            token_usage_db["completion_tokens"] += completion_tokens
            token_usage_db["cost_usd"] = round(token_usage_db["cost_usd"] + cost, 6)
            token_usage_db["total_calls"] += 1

            raw_content = response.choices[0].message.content or "{}"
            try:
                parsed_content = json.loads(raw_content)
            except Exception:
                parsed_content = {"response": raw_content}

            return {
                "status": "success",
                "model_used": model,
                "response": parsed_content,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "cost_usd": round(cost, 6),
                },
            }
        except Exception as e:
            logger.warning(f"Model {model} failed: {e}. Trying fallback...")
            continue

    raise HTTPException(status_code=503, detail="All AI models are currently unavailable.")


@app.post("/ask", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    settings: Annotated[Settings, Depends(get_settings)],
):
    """Answers compliance queries with page-level citations from the 500+ page regulatory corpus.

    Retrieves top-k relevant chunks from pgvector/in-memory store, builds context,
    and invokes the LLM fallback chain.
    """
    # 1. Retrieve relevant chunks using dense embeddings
    query_vec = get_embedding(request.query)
    chunks = search_chunks(query_vec, top_k=request.top_k)

    # 2. Extract citations
    citations: list[Citation] = []
    seen_citations = set()
    context_blocks = []

    for c in chunks:
        doc = c["document_name"]
        page = c["page_number"]
        section = c.get("section_heading") or ""
        key = (doc, page)
        if key not in seen_citations:
            seen_citations.add(key)
            citations.append(Citation(document=doc, page=page, section=section))

        context_blocks.append(
            f"--- [Document: {doc} | Page: {page} | Section: {section}] ---\n{c['chunk_text']}"
        )

    context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant documents found."

    # 3. Formulate prompt for LLM
    system_prompt = (
        "You are ScrapLedger, an expert regulatory compliance assistant for Indian "
        "waste management and Extended Producer Responsibility (EPR) regulations (CPCB / MoEFCC).\n"
        "Answer the question accurately based on the provided statutory context.\n"
        "Always cite the relevant document name and page number for each legal obligation or penalty.\n"
        "If the context does not contain the answer, state what is known and specify "
        "that the statutory documents do not provide this information."
    )

    user_prompt = f"Statutory Context:\n{context_str}\n\nQuestion: {request.query}\nAnswer:"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    models = [request.model] if request.model else []
    for model in [settings.primary_model] + FALLBACK_MODELS:
        if model not in models:
            models.append(model)

    for model in models:
        try:
            extra_kwargs: dict[str, Any] = {}
            if "gemini" in model:
                gemini_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
                if gemini_key:
                    extra_kwargs["api_key"] = gemini_key

            response = completion(
                model=model,
                messages=messages,
                timeout=settings.llm_timeout,
                num_retries=settings.llm_retries,
                **extra_kwargs,
            )

            prompt_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
            completion_tokens = getattr(response.usage, "completion_tokens", 0) or 0
            total_tokens = getattr(
                response.usage, "total_tokens", prompt_tokens + completion_tokens
            ) or 0

            try:
                cost = completion_cost(completion_response=response) or 0.0
            except Exception:
                cost = 0.0

            # Update usage stats
            token_usage_db["total_tokens"] += total_tokens
            token_usage_db["prompt_tokens"] += prompt_tokens
            token_usage_db["completion_tokens"] += completion_tokens
            token_usage_db["cost_usd"] = round(token_usage_db["cost_usd"] + cost, 6)
            token_usage_db["total_calls"] += 1

            answer_text = response.choices[0].message.content or ""

            return AskResponse(
                query=request.query,
                answer=answer_text.strip(),
                citations=citations,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "cost_usd": round(cost, 6),
                },
            )
        except Exception as e:
            logger.warning(f"Model {model} failed in /ask: {e}. Trying fallback...")
            continue

    raise HTTPException(status_code=503, detail="All AI models are currently unavailable.")
