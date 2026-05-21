# Single-GPU Plan

The first GPU milestone is simple: prove the core performance story on one NVIDIA GPU before adding
more serving infrastructure.

This can run on a local GPU workstation, a rented GPU pod, or a cloud GPU VM. The important part is
to keep the first pass measurable and repeatable.

## Goal

Run the PyTorch/FastAPI baseline on one GPU, expose the API, run the benchmark client, and save
reports under `docs/reports`.

## Experiments To Capture

| Experiment | Change |
| --- | --- |
| Baseline | Dense model, low concurrency |
| Concurrency | 1, 2, 4, 8, 16 concurrent requests |
| Output length | 32, 64, 128, 256 generated tokens |
| Prompt shape | support agent, infra debug, long summary |
| Architecture | dense model versus MoE model that fits the GPU |

## What To Watch

- p95 and p99 latency
- aggregate output tokens/sec
- GPU memory allocated/reserved
- failed requests
- cold start model download time
- whether tokenization or generation dominates

