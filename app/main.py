import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from litellm import completion, completion_cost

app = FastAPI(title="ScrapLedger API")

# In-memory database for tracking real API usage and costs
token_usage_db = {
    "total_tokens": 0,
    "cost_usd": 0.0
}

class ChatRequest(BaseModel):
    query: str

class UsageResponse(BaseModel):
    total_tokens: int
    cost_usd: float

@app.get("/health")
def health_check():
    """Health check endpoint for Docker and CI/CD."""
    return {"status": "ok", "app": "ScrapLedger", "environment": "local"}

@app.get("/usage", response_model=UsageResponse)
def get_usage():
    """Returns actual LLM token usage and accumulated cost."""
    return token_usage_db

@app.post("/chat")
def chat_with_agent(request: ChatRequest):
    """
    Calls an LLM to answer compliance queries and returns structured JSON.
    Includes timeouts, 3 retries, and a fallback model.
    """
    # Define primary model (Gemini) and fallback models (OpenAI/Anthropic)
    models = ["gemini/gemini-1.5-flash", "gpt-4o-mini", "claude-3-haiku-20240307"]
    
    for model in models:
        try:
            # Attempt LLM call with a 10-second timeout and 3 retries
            response = completion(
                model=model,
                messages=[
                    {"role": "system", "content": "You are ScrapLedger, a regulatory compliance assistant. Always return answers in clear, structured JSON format."},
                    {"role": "user", "content": request.query}
                ],
                response_format={"type": "json_object"},
                timeout=10.0,
                num_retries=3
            )
            
            # Calculate tokens and exact cost for this specific call
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = prompt_tokens + completion_tokens
            cost = completion_cost(completion_response=response)
            
            # Update global cost log
            token_usage_db["total_tokens"] += total_tokens
            if cost:
                token_usage_db["cost_usd"] += cost

            # Return structured JSON
            return {
                "status": "success",
                "model_used": model,
                "response": response.choices[0].message.content,
                "usage": {
                    "tokens": total_tokens,
                    "cost": cost
                }
            }
            
        except Exception as e:
            # If the model fails or times out, the loop continues to the fallback model
            print(f"Model {model} failed: {e}. Trying fallback...")
            continue
            
    # If all models in the fallback chain fail
    raise HTTPException(status_code=503, detail="All AI models are currently unavailable.")