.PHONY: install run lint test format clean docker-build docker-run

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest --maxfail=1 --disable-warnings -q

lint:
	ruff check .

format:
	ruff format .

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache

docker-build:
	docker build -t sentiment-spotlight .

docker-run:
	docker run --rm -p 8000:8000 sentiment-spotlight
