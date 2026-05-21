from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_perf_lab.config import settings


@dataclass(frozen=True)
class GenerationResult:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    tokens_per_second: float
    device: str
    gpu_memory_allocated_mb: float | None
    gpu_memory_reserved_mb: float | None


def _resolve_device(requested: str) -> str:
    if requested == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("DEVICE=cuda was requested, but torch.cuda.is_available() is false.")
    return requested


def _resolve_dtype(device: str, requested: str) -> Any:
    if requested == "float16":
        return torch.float16
    if requested == "bfloat16":
        return torch.bfloat16
    if requested == "float32":
        return torch.float32
    if requested == "auto" and device == "cuda":
        return torch.float16
    return torch.float32


class ModelRuntime:
    def __init__(self) -> None:
        self.device = _resolve_device(settings.device)
        torch_dtype = _resolve_dtype(self.device, settings.torch_dtype)

        self.tokenizer = AutoTokenizer.from_pretrained(settings.model_id)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(settings.model_id, torch_dtype=torch_dtype)
        self.model.to(self.device)
        self.model.eval()

    def generate(
        self,
        prompt: str,
        max_new_tokens: int | None = None,
        temperature: float = 0.0,
    ) -> GenerationResult:
        max_new_tokens = max_new_tokens or settings.default_max_new_tokens

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=settings.max_input_tokens,
        ).to(self.device)

        if self.device == "cuda":
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()

        generation_args = {
            **inputs,
            "max_new_tokens": max_new_tokens,
            "do_sample": temperature > 0,
            "pad_token_id": self.tokenizer.eos_token_id,
        }
        if temperature > 0:
            generation_args["temperature"] = temperature

        start = time.perf_counter()
        with torch.inference_mode():
            output_ids = self.model.generate(**generation_args)

        if self.device == "cuda":
            torch.cuda.synchronize()

        latency_ms = (time.perf_counter() - start) * 1000
        input_tokens = int(inputs["input_ids"].shape[-1])
        output_tokens = int(output_ids.shape[-1] - input_tokens)
        text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        tokens_per_second = output_tokens / (latency_ms / 1000) if latency_ms > 0 else 0.0

        return GenerationResult(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            tokens_per_second=tokens_per_second,
            device=self.device,
            gpu_memory_allocated_mb=self._gpu_allocated_mb(),
            gpu_memory_reserved_mb=self._gpu_reserved_mb(),
        )

    def _gpu_allocated_mb(self) -> float | None:
        if self.device != "cuda":
            return None
        return torch.cuda.max_memory_allocated() / 1024 / 1024

    def _gpu_reserved_mb(self) -> float | None:
        if self.device != "cuda":
            return None
        return torch.cuda.max_memory_reserved() / 1024 / 1024


runtime = ModelRuntime()

