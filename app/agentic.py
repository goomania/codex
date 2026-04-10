"""Lightweight agent orchestration utilities for the Streamlit app."""

from __future__ import annotations

import ast
import operator
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

import httpx

from . import sentiment

DB_PATH = Path(".data") / "agent_memory.db"


@dataclass(frozen=True)
class ToolResult:
    """Result container for tool execution."""

    tool_name: str
    output: str


def _ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_note(note: str) -> ToolResult:
    """Persist a note into local SQLite memory."""

    cleaned = note.strip()
    if not cleaned:
        return ToolResult("db.save_note", "I could not save an empty note.")

    _ensure_db()
    timestamp = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO notes(body, created_at) VALUES(?, ?)", (cleaned, timestamp))
        conn.commit()
    return ToolResult("db.save_note", f"Saved note: {cleaned}")


def search_notes(query: str, limit: int = 5) -> ToolResult:
    """Search notes stored in local SQLite memory."""

    cleaned = query.strip()
    if not cleaned:
        return ToolResult("db.search_notes", "Please provide a search phrase.")

    _ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT body, created_at FROM notes WHERE body LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{cleaned}%", limit),
        ).fetchall()

    if not rows:
        return ToolResult("db.search_notes", f"No notes found matching '{cleaned}'.")

    lines = [f"- {body} (saved {created_at})" for body, created_at in rows]
    return ToolResult("db.search_notes", "\n".join(lines))


_ALLOWED_OPERATORS: dict[type[ast.AST], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}


def _eval_math(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_math(node.operand)
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError("Unsupported operator in expression.")
        return _ALLOWED_OPERATORS[op_type](_eval_math(node.left), _eval_math(node.right))
    raise ValueError("Unsupported expression.")


def calculate(expression: str) -> ToolResult:
    """Safely evaluate a simple arithmetic expression."""

    try:
        parsed = ast.parse(expression, mode="eval")
        value = _eval_math(parsed.body)
    except Exception as exc:
        return ToolResult("math.calculate", f"Could not evaluate expression: {exc}")
    return ToolResult("math.calculate", f"{expression} = {value}")


def fetch_joke() -> ToolResult:
    """Fetch a short joke from a public API."""

    url = "https://api.chucknorris.io/jokes/random"
    try:
        response = httpx.get(url, timeout=8.0)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return ToolResult("api.fetch_joke", f"API call failed: {exc}")

    joke = payload.get("value", "No joke returned.")
    return ToolResult("api.fetch_joke", joke)


def get_utc_time() -> ToolResult:
    """Return current UTC timestamp."""

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    return ToolResult("system.time", f"Current UTC time is {now}")


def analyze_sentiment(text: str) -> ToolResult:
    """Analyze sentiment via existing VADER utility."""

    try:
        result = sentiment.analyze_text(text)
    except ValueError as exc:
        return ToolResult("nlp.sentiment", str(exc))

    output = (
        f"Sentiment: {result.label} (compound={result.score:.3f}, "
        f"pos={result.positive:.3f}, neu={result.neutral:.3f}, neg={result.negative:.3f})"
    )
    return ToolResult("nlp.sentiment", output)


def _extract_after_prefix(prompt: str, prefixes: Iterable[str]) -> str:
    lowered = prompt.lower()
    for prefix in prefixes:
        idx = lowered.find(prefix)
        if idx >= 0:
            return prompt[idx + len(prefix) :].strip(" :")
    return ""


def run_agent(prompt: str) -> list[ToolResult]:
    """Route the user prompt to one or more tools and return a trace."""

    lowered = prompt.lower().strip()
    if not lowered:
        return [ToolResult("agent", "Please enter a prompt.")]

    if any(token in lowered for token in ("save note", "remember", "store this")):
        note = _extract_after_prefix(lowered, ("save note", "remember", "store this"))
        note_text = note or prompt
        return [save_note(note_text)]

    if any(token in lowered for token in ("find note", "search notes", "recall")):
        query = _extract_after_prefix(lowered, ("find note", "search notes", "recall"))
        return [search_notes(query or prompt)]

    if any(token in lowered for token in ("calculate", "math", "solve")):
        expr = _extract_after_prefix(prompt, ("calculate", "solve"))
        expr = expr or prompt
        return [calculate(expr)]

    if any(token in lowered for token in ("sentiment", "tone", "feel")):
        return [analyze_sentiment(prompt)]

    if any(token in lowered for token in ("joke", "funny")):
        return [fetch_joke()]

    if any(token in lowered for token in ("time", "date", "utc")):
        return [get_utc_time()]

    return [
        ToolResult(
            "agent",
            "I can use tools for math, sentiment, API jokes, UTC time, and SQLite notes. "
            "Try prompts like 'calculate 9*(3+2)' or 'save note: buy milk'.",
        )
    ]
