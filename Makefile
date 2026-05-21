.PHONY: install run benchmark benchmark-support benchmark-infra benchmark-summary docker-build k8s-apply k8s-delete verify

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -e .

run:
	. .venv/bin/activate && uvicorn llm_perf_lab.app:app --host 0.0.0.0 --port 8000

benchmark:
	. .venv/bin/activate && python scripts/benchmark_http.py --requests 20 --concurrency 4 --out docs/reports/local-short-chat

benchmark-support:
	. .venv/bin/activate && python scripts/benchmark_http.py --profile support_agent --requests 30 --concurrency 3 --max-new-tokens 160 --out docs/reports/support-agent

benchmark-infra:
	. .venv/bin/activate && python scripts/benchmark_http.py --profile infra_debug --requests 30 --concurrency 3 --max-new-tokens 160 --out docs/reports/infra-debug

benchmark-summary:
	. .venv/bin/activate && python scripts/benchmark_http.py --profile long_context_summary --requests 10 --concurrency 2 --max-new-tokens 220 --out docs/reports/long-context-summary

docker-build:
	docker build -t gpu-inference-workbench:local .

k8s-apply:
	kubectl apply -f k8s/

k8s-delete:
	kubectl delete -f k8s/

verify:
	env PYTHONPYCACHEPREFIX=.pycache python3 -m compileall src scripts
