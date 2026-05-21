# Phi-2 Long-Context Sweep

This sweep keeps the model, backend, GPU, concurrency, request count, and output cap fixed while
changing the input token cap.

Setup:

- Model: `microsoft/phi-2`
- Architecture: dense
- Backend: PyTorch + Hugging Face Transformers
- GPU: RTX 4090
- Profile: `long_context_summary`
- Requests: 10
- Concurrency: 2
- Max output tokens/request: 220

| Input cap | Avg input/request | Avg output/request | p95 latency | Aggregate output tok/s |
| ---: | ---: | ---: | ---: | ---: |
| 512 | 512.0 | 220.0 | 4180.78 ms | 112.552 |
| 1024 | 1024.0 | 220.0 | 4428.645 ms | 105.821 |
| 2048 | 2048.0 | 220.0 | 4561.256 ms | 96.672 |

Early read:

As the per-request input cap increases from 512 to 2048 tokens, aggregate output throughput drops
from 112.552 to 96.672 tokens/sec and p95 latency increases from 4180.78 ms to 4561.256 ms.
