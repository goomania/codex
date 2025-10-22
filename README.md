# Sentiment Spotlight

Sentiment Spotlight is a small but complete web application that allows users to paste
free-form text and instantly receive a sentiment classification powered by the
[VADER](https://github.com/cjhutto/vaderSentiment) rule-based model. The project includes
an interactive FastAPI web experience, a JSON API, automated tests, infrastructure-as-code
artifacts for deployment, and documentation describing how to operate the service.

![Screenshot of the Sentiment Spotlight interface](docs/images/ui-overview.png)

## Features

- **Interactive UI** – Submit text through a friendly web form and view the predicted
  sentiment and polarity scores.
- **JSON API** – Integrate with other services via `POST /api/sentiment`.
- **Production ready** – Health-check endpoint, Docker image, and CI workflow are included.
- **Tested** – Unit tests for the sentiment logic and integration tests for the API routes.

## Project layout

```
app/
├── __init__.py          # Application package entrypoint
├── main.py              # FastAPI app definition and routes
├── schemas.py           # Pydantic models for the JSON API
├── sentiment.py         # VADER-powered sentiment helpers
├── static/              # CSS assets
└── templates/           # Jinja2 templates for the HTML UI

docs/
├── DEPLOYMENT.md        # Deployment and operations guide
└── images/              # Generated screenshots and diagrams

tests/
├── test_api.py          # Integration tests for HTTP endpoints
└── test_sentiment.py    # Unit tests for sentiment utilities
```

## Getting started

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application locally

```bash
uvicorn app.main:app --reload
```

Visit <http://127.0.0.1:8000> in your browser and submit any text to see the
classification.

## How to run tests

The repository includes a `Makefile` shortcut, but you can also call `pytest` directly.

```bash
make test
# or
pytest
```

## Docker usage

A multi-stage `Dockerfile` is provided for container-based deployments.

```bash
docker build -t sentiment-spotlight .
docker run --rm -p 8000:8000 sentiment-spotlight
```

The container will expose the service at <http://127.0.0.1:8000>.

## Continuous integration

The GitHub Actions workflow under `.github/workflows/ci.yml` installs dependencies and
runs the test suite on every push to ensure the application remains healthy.

## Next steps

- Configure HTTPS termination using your hosting provider of choice.
- Add authentication if you plan to expose the API publicly.
- Extend the UI with charts or historical tracking of submitted text.

## License

This project is released under the MIT License. See [`LICENSE`](LICENSE) for details.
