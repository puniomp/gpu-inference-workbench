# GPU Inference Workbench

I kept seeing the same question underneath every LLM demo: what happens when this has to be fast?

This project is my attempt to answer that question from the bottom up: start with one GPU, serve
real applied AI prompts, measure latency and throughput, compare dense and MoE models, and keep
following the bottlenecks.

The fun part, to me, is the space between "the model answered" and "this system is fast, observable,
cost-aware, and explainable." This repo is where I am working through that space in public.

The first milestone is intentionally small and real:

- Serve a Hugging Face causal language model through FastAPI.
- Compare dense and MoE models on applied AI workloads.
- Capture latency, throughput, generated tokens, device, and GPU memory when CUDA is available.
- Run concurrent benchmark workloads and export JSON, CSV, and Markdown reports.
- Package the service with Docker.
- Keep Kubernetes as an optional scale-out chapter, not the center of the project.
- Leave clear extension points for Triton Inference Server and TensorRT-LLM.

## Why This Exists

I am using this project as a way to get sharper at the parts of AI infrastructure that feel both
practical and a little mysterious from the outside:

- What makes one inference path faster or cheaper than another?
- Where does latency actually come from?
- What changes when I compare dense models against mixture-of-experts models?
- How do batching, prompt length, model size, GPU memory, and concurrency interact?
- What changes when the service moves from a single GPU to a containerized serving path?
- How do I explain the results clearly enough that another engineer could act on them?

The personal arc is simple:

**LLM app builder -> inference benchmarker -> GPU systems troubleshooter -> AI infrastructure writer**

This is not meant to be a polished benchmark suite on day one. It is meant to be a serious,
repeatable workbench that gets better every time I learn something.

## Quick Start

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Start the service:

```bash
uvicorn llm_perf_lab.app:app --host 0.0.0.0 --port 8000
```

Run a smoke request:

```bash
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/generate \
  -H 'content-type: application/json' \
  -d '{"prompt":"Explain GPU inference bottlenecks in three bullets.","max_new_tokens":80}'
```

Run a benchmark:

```bash
python scripts/benchmark_http.py \
  --url http://localhost:8000/generate \
  --profile support_agent \
  --requests 30 \
  --concurrency 3 \
  --max-new-tokens 160 \
  --model-id microsoft/phi-2 \
  --model-architecture dense \
  --out docs/reports/dense-support-agent
```

## Model Selection

By default the service uses `sshleifer/tiny-gpt2` so the path works on CPU. For more realistic GPU
benchmarking, set:

```bash
export MODEL_ID=microsoft/phi-2
export DEVICE=cuda
```

Use a model your hardware can actually run. The goal is not to chase the biggest model first; the
goal is to build a repeatable measurement harness.

## Current Milestones

- M1: PyTorch/FastAPI inference service
- M2: HTTP benchmark runner with p50/p95/p99 and tokens/sec
- M3: Single-GPU benchmark
- M4: Dense vs MoE applied AI experiment
- M5: Docker image
- M6: Triton baseline
- M7: TensorRT-LLM baseline
- M8: Kubernetes manifests, if orchestration becomes the question
- M9: Azure GPU deployment notes

## Repo Layout

```text
src/llm_perf_lab/       FastAPI service and model runtime
scripts/                Benchmark and helper scripts
k8s/                    Kubernetes deployment scaffold
triton/                 Triton Inference Server notes and placeholders
docs/reports/           Generated benchmark reports
docs/experiments/       Experiment plans and interpretation guides
```

## Recommended Path

Start with a single GPU, then add complexity only when it answers a real question:

1. Run the FastAPI/PyTorch baseline on one GPU.
2. Capture benchmark reports for applied AI workload profiles.
3. Compare dense and MoE models under the same workload shape.
4. Build a Docker image once the local scripts are stable.
5. Add Triton or TensorRT-LLM when serving/runtime optimization becomes the question.
6. Add Kubernetes later only when orchestration, scheduling, or multi-replica scale becomes the question.

See:

- `docs/single-gpu.md`
- `docs/experiments/dense-vs-moe.md`
- `docs/kubernetes-roadmap.md`
