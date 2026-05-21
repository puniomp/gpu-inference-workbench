# Triton Track

This directory is for a future serving-runtime comparison.

The goal is to compare the PyTorch/FastAPI baseline against NVIDIA Triton Inference Server using the
same applied AI workload profiles:

- p50/p95/p99 latency
- aggregate requests/sec
- aggregate output tokens/sec
- GPU memory behavior
- batching impact
- queueing or failure behavior under concurrency

