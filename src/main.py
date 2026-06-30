import time, uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import Response

app = FastAPI(title="Cloud-Native AI Platform", version="1.0.0", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

REQUEST_COUNT = Counter("ai_platform_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("ai_platform_request_duration_seconds", "Request latency", ["endpoint"], buckets=[0.01,0.05,0.1,0.25,0.5,1,2.5,5])
INFERENCE_COUNT = Counter("ai_platform_inference_total", "AI inference requests", ["model", "status"])
INFERENCE_LATENCY = Histogram("ai_platform_inference_duration_seconds", "Inference latency", ["model"])

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(duration)
    response.headers["X-Response-Time"] = f"{duration*1000:.2f}ms"
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    return response

@app.get("/health", tags=["Observability"])
async def health():
    return {"status": "healthy", "service": "cloud-native-ai-platform", "version": "1.0.0"}

@app.get("/ready", tags=["Observability"])
async def readiness():
    return {"status": "ready"}

@app.get("/live", tags=["Observability"])
async def liveness():
    return {"status": "alive"}

@app.get("/metrics", tags=["Observability"])
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

class InferenceRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4096)
    model: str = Field("gpt-4o-mini")
    max_tokens: int = Field(256, ge=1, le=4096)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    context: Optional[str] = None

class InferenceResponse(BaseModel):
    request_id: str
    model: str
    output: str
    tokens_used: int
    latency_ms: float

SUPPORTED_MODELS = {
    "gpt-4o-mini":    {"provider": "openai",      "context_window": 128000},
    "claude-3-haiku": {"provider": "anthropic",   "context_window": 200000},
    "llama-3-8b":     {"provider": "self-hosted", "context_window": 8192},
}

@app.post("/api/v1/infer", response_model=InferenceResponse, tags=["Inference"])
async def infer(req: InferenceRequest):
    if req.model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail=f"Model not supported. Available: {list(SUPPORTED_MODELS)}")
    start = time.perf_counter()
    output = f"[{req.model}] Response to: '{req.prompt[:60]}' -- Plug in OpenAI/Anthropic/vLLM SDK here."
    latency_ms = (time.perf_counter() - start) * 1000
    INFERENCE_COUNT.labels(model=req.model, status="success").inc()
    INFERENCE_LATENCY.labels(model=req.model).observe(latency_ms / 1000)
    return InferenceResponse(
        request_id=str(uuid.uuid4()), model=req.model, output=output,
        tokens_used=len(req.prompt.split()) + len(output.split()),
        latency_ms=round(latency_ms, 2),
    )

@app.get("/api/v1/models", tags=["Inference"])
async def list_models():
    return {"models": [{"id": k, **v} for k, v in SUPPORTED_MODELS.items()]}
