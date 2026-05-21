from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from llm_perf_lab.config import settings
from llm_perf_lab.runtime import runtime


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    max_new_tokens: int | None = Field(default=None, ge=1, le=2048)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class GenerateResponse(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    tokens_per_second: float
    device: str
    gpu_memory_allocated_mb: float | None
    gpu_memory_reserved_mb: float | None


app = FastAPI(
    title="GPU Inference Workbench",
    version="0.1.0",
    description="A small LLM inference service designed for applied AI and GPU performance benchmarking.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "model_id": settings.model_id,
        "device": runtime.device,
    }


@app.post("/generate")
def generate(request: GenerateRequest) -> GenerateResponse:
    result = runtime.generate(
        prompt=request.prompt,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
    )
    return GenerateResponse(**result.__dict__)
