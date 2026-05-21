# Runtime Notes

The current backend is intentionally simple:

```text
FastAPI -> Hugging Face Transformers -> PyTorch CUDA -> model.generate()
```

That gives me a baseline I can understand before swapping in more specialized inference runtimes.

## Why Kernels Matter

LLM inference is not only about the model. It is also about how the model's operations run on the
GPU.

A fused kernel combines multiple GPU operations into one kernel launch. Instead of doing:

```text
operation A -> write to memory
operation B -> read from memory -> write to memory
operation C -> read from memory
```

the runtime may combine work so the GPU does less memory traffic and fewer launches:

```text
operation A + operation B + operation C
```

That can improve latency and throughput because the model spends less time moving intermediate
values around and more time doing useful work.

In LLM inference, kernel/runtime optimizations often show up around:

- attention
- layer normalization
- rotary embeddings
- MLP/feed-forward blocks
- activation functions
- quantized matrix multiplication
- sampling and logits processing
- KV cache reads and writes

## Current Baseline

The PyTorch/Transformers path is useful because it answers:

> How fast is the straightforward implementation?

It is not the fastest possible serving path, and that is the point. I need a plain baseline before I
can make a meaningful claim about what a more optimized runtime improves.

## Runtime Comparisons I May Try

| Runtime | What It Tests |
| --- | --- |
| PyTorch + Transformers | Baseline eager inference path |
| `torch.compile` | Compiler-driven graph optimization and possible fusion |
| vLLM | LLM-oriented serving, paging, batching, and KV cache management |
| Triton Inference Server | Production inference serving, model repositories, dynamic batching |
| TensorRT-LLM | NVIDIA-optimized inference engines and fused kernels |

## Experiment Shape

Use the same workload profiles and compare each backend against the baseline:

- `support_agent`
- `infra_debug`
- `long_context_summary`

Hold these constant:

- model
- GPU
- request count
- concurrency
- max output tokens
- input token cap

Measure:

- p50/p95/p99 latency
- aggregate output tokens/sec
- GPU memory
- failed requests
- cold start or compile time
- operational complexity

## What I Am Looking For

The useful question is not "which backend is cool?" The useful question is:

> What does this runtime make faster, what does it make harder, and under which workload does the
> tradeoff show up?

If fused kernels, better attention implementations, or smarter KV cache handling matter, they should
show up as lower latency, higher throughput, better concurrency behavior, or lower memory pressure
under the same applied AI workload.
