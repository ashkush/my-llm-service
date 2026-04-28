import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from .engine import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model in background thread so the server starts immediately
    # This prevents Azure startup probe timeouts during model download
    thread = threading.Thread(target=engine.load_model, daemon=True)
    thread.start()
    yield
    # Clean up (if needed) on shutdown
    if engine.generator:
        del engine.generator

app = FastAPI(title="Azure AI DevOps Service", lifespan=lifespan)

class QueryRequest(BaseModel):
    prompt: str
    max_tokens: int = 150

@app.get("/health")
def health_check():
    """Crucial for Azure Container Apps health probes.
    Returns 200 immediately so startup probes pass,
    and reports whether model is ready for inference."""
    return {"status": "healthy", "model_loaded": engine.generator is not None}

@app.post("/predict")
async def predict(request: QueryRequest):
    if engine.generator is None:
        raise HTTPException(status_code=503, detail="Model is still loading. Please try again in a few minutes.")
    
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    try:
        response = engine.generate_text(request.prompt, request.max_tokens)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))