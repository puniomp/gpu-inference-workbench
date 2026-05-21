# Dense vs MoE For Applied AI Inference

This experiment compares dense and mixture-of-experts models on application-shaped workloads rather
than generic prompts.

The point is not to crown one architecture as universally better. I have seen enough enterprise
GenAI conversations to know that the useful question is usually more grounded: given a real
application shape, what does this model choice do to latency, throughput, memory, cost, and the
quality bar the team actually cares about?

I am especially interested in the gap between model-card enthusiasm and production behavior. A
model can look great in a launch post, but the applied AI question is messier: does it behave well
when the prompt includes retrieved context, the answer needs to be concise, traffic arrives in
bursts, and the team still has to explain the bill?

## Question

For applied AI workloads, when does a MoE model behave differently from a dense model?

More specifically:

- Does the architecture change the latency profile for RAG-style prompts?
- Does MoE help enough on output quality or throughput to justify operational complexity?
- Does total parameter memory matter more than active parameters on a single GPU?
- Which workload shape makes the tradeoff visible first?

## Hypothesis

MoE models can offer strong quality for the amount of active compute per token, but they may still
carry real memory and serving complexity because the full set of experts has to be available. On a
single GPU, that tradeoff should show up in memory pressure, cold start behavior, and latency under
concurrency.

## Workload Profiles

Use these benchmark profiles:

| Profile | Applied AI Scenario | What It Stresses |
| --- | --- | --- |
| `support_agent` | RAG-style customer support answer | instruction following, context use, concise response |
| `infra_debug` | AI infrastructure troubleshooting assistant | technical reasoning, practical recommendations |
| `long_summary` | incident or architecture review summarization | long input, context handling, output structure |

These are intentionally close to the kinds of workloads teams reach for when they move from
"let's try a chat model" to "we need an assistant that helps employees, engineers, or customers do
real work." The prompts are not synthetic trivia; they are meant to expose behavior around context,
reasoning, concision, and operational usefulness.

## Candidate Models

Pick models that fit the GPU you actually have.

| Architecture | Example | Notes |
| --- | --- | --- |
| Dense | `microsoft/phi-2` | Simple starter baseline, lighter than modern 7B models |
| Dense | Qwen or Mistral dense instruct model | Better applied-AI comparison if VRAM allows |
| MoE | Mixtral instruct variant | Classic MoE comparison, but memory can be heavy |
| MoE | Qwen MoE instruct variant | Potentially better modern MoE path if available for your GPU |

## Run Pattern

Start the service with a dense model:

```bash
export MODEL_ID=<dense-model-id>
export DEVICE=cuda
uvicorn llm_perf_lab.app:app --host 0.0.0.0 --port 8000
```

Run the applied AI profiles:

```bash
python scripts/benchmark_http.py \
  --url http://localhost:8000/generate \
  --profile support_agent \
  --requests 30 \
  --concurrency 3 \
  --max-new-tokens 160 \
  --model-id <dense-model-id> \
  --model-architecture dense \
  --out docs/reports/dense-support-agent
```

Restart the service with a MoE model:

```bash
export MODEL_ID=<moe-model-id>
export DEVICE=cuda
uvicorn llm_perf_lab.app:app --host 0.0.0.0 --port 8000
```

Run the same profile:

```bash
python scripts/benchmark_http.py \
  --url http://localhost:8000/generate \
  --profile support_agent \
  --requests 30 \
  --concurrency 3 \
  --max-new-tokens 160 \
  --model-id <moe-model-id> \
  --model-architecture moe \
  --out docs/reports/moe-support-agent
```

Repeat for:

- `infra_debug`
- `long_summary`

## What To Compare

| Dimension | Why It Matters |
| --- | --- |
| p50 latency | Typical user experience |
| p95/p99 latency | Tail behavior under concurrency |
| output tokens/sec | Generation throughput |
| input tokens | Prompt/context pressure |
| GPU memory | Whether the model fits comfortably |
| failures | Whether the model is operationally realistic |
| answer quality notes | Whether performance tradeoffs are worth it |

I want the quality notes to stay practical. Not "which answer sounds cooler," but:

- Did it follow the requested structure?
- Did it use the provided context instead of hallucinating around it?
- Did it give an answer a support engineer, cloud architect, or product team could act on?
- Did it stay concise under a realistic token budget?
- Did the better answer cost meaningfully more latency or memory?

That is the applied AI tradeoff I care about.

