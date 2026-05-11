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


device-replay:
	c++ -std=c++17 device_replay/replay_device_trace.cpp -o device_replay/replay_device_trace
	./device_replay/replay_device_trace || true
	cc -std=c11 device_replay/replay_result.c device_replay/replay_c_api_demo.c -o device_replay/replay_c_api_demo
	./device_replay/replay_c_api_demo
