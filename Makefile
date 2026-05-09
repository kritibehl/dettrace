.PHONY: install test benchmark docker run

install:
	cd dettrace_platform && python3 -m pip install -r requirements.txt pytest httpx

test: install
	cd dettrace_platform && PYTHONPATH=. python3 -m pytest -q tests/test_api_workflows.py

benchmark: install
	PYTHONPATH=. python3 scripts/benchmark_api.py

docker:
	docker build -t dettrace-platform .

run:
	cd dettrace_platform && uvicorn app.main:app --host 127.0.0.1 --port 8010
