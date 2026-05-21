# Kubernetes Scaling Roadmap

Kubernetes is useful later, but it is not the center of this project.

The better path is to separate two learning curves:

1. Learn GPU inference on a single GPU.
2. Learn Kubernetes deployment mechanics without requiring GPU quota.
3. Combine them later only when orchestration, scheduling, or multi-replica scale becomes the
   actual question.

## When Kubernetes Becomes Worth It

Use Kubernetes when the question becomes:

- multiple replicas
- GPU scheduling
- rolling updates
- service exposure
- platform observability
- autoscaling behavior
- cost and utilization across workloads

## Practical Ladder

### Stage 1: Single GPU

Prove the model and benchmark logic.

### Stage 2: Docker

Package the app:

```bash
make docker-build
docker run --gpus all -p 8000:8000 gpu-inference-workbench:local
```

### Stage 3: Kubernetes Without GPU

Use a cheap local or non-GPU cluster to learn deployment mechanics:

```bash
kubectl apply -f k8s/
kubectl port-forward service/gpu-inference-workbench 8000:8000
```

### Stage 4: Kubernetes With GPU

Move to a GPU node pool and request `nvidia.com/gpu: "1"` only when orchestration is the question.
