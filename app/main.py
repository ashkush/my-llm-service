from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from .engine import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs ONCE when the container starts
    engine.load_model()
    yield
    # Clean up (if needed) on shutdown
    del engine.generator

app = FastAPI(title="Azure AI DevOps Service", lifespan=lifespan)

class QueryRequest(BaseModel):
    prompt: str
    max_tokens: int = 150

@app.get("/health")
def health_check():
    """Crucial for Azure Container Apps health probes"""
    return {"status": "healthy", "model_loaded": engine.generator is not None}

@app.post("/predict")
async def predict(request: QueryRequest):
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    try:
        response = engine.generate_text(request.prompt, request.max_tokens)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))