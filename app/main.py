"""FastAPI application exposing HTML and JSON interfaces for sentiment analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import sentiment
from .schemas import SentimentRequest, SentimentResponse

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Sentiment Spotlight",
    description="A tiny FastAPI app that classifies user-provided text with the VADER sentiment analyzer.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/health", summary="Health check")
async def health() -> Dict[str, str]:
    """Return a basic readiness indicator for uptime monitoring."""

    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, summary="Render the web form")
async def render_form(request: Request) -> HTMLResponse:
    """Render the landing page with the sentiment analysis form."""

    context: Dict[str, Any] = {"request": request, "result": None, "error": None, "submitted_text": ""}
    return templates.TemplateResponse(request, "index.html", context)


@app.post("/", response_class=HTMLResponse, summary="Analyze text via the web form")
async def analyze_form(request: Request, text: str = Form(..., min_length=1)) -> HTMLResponse:
    """Handle the form submission and render the result inline."""

    context: Dict[str, Any] = {"request": request, "submitted_text": text}
    try:
        result = sentiment.analyze_text(text)
    except ValueError as exc:  # pragma: no cover - defensive guard
        context.update({"result": None, "error": str(exc)})
    else:
        context.update({"result": result, "error": None})
    return templates.TemplateResponse(request, "index.html", context)


@app.post("/api/sentiment", response_model=SentimentResponse, summary="Analyze text via JSON")
async def analyze_api(payload: SentimentRequest) -> SentimentResponse:
    """Analyze text supplied as JSON and return structured sentiment data."""

    try:
        result = sentiment.analyze_text(payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return SentimentResponse(**result.__dict__)


if __name__ == "__main__":  # pragma: no cover - script convenience
    import uvicorn

    uvicorn.run("app.main:app", reload=True, host="0.0.0.0", port=8000)
