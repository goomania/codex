# LangChain Agent Mini Project

This mini project demonstrates how to assemble a tiny LangChain agent that can
use a Python tool.  The goal is to give you a script you can run in class to
show the moving parts of LangChain—prompts, models, tools, and the agent
executor—without relying on external APIs.

## What the demo does

* Defines a `character_count` tool that reports the number of characters in a
  piece of text.
* Builds a tool-calling agent using LangChain's modular agent interface.
* Runs the agent against a sample question and prints the final answer.

The default configuration ships with a lightweight, deterministic chat model so
the demo can run without network access.  You can swap in a real chat model
that supports structured tool calls (for example
`langchain_openai.ChatOpenAI`) by passing it into `build_demo_agent`.

## Running the demo

```bash
pip install -r requirements.txt
python -m mini_projects.langchain_agent.agent_demo
```

The script prints the agent's reasoning steps followed by the final answer.

To experiment with a real model, set the `OPENAI_API_KEY` environment variable
and edit `build_demo_agent` to use `ChatOpenAI`:

```python
from langchain_openai import ChatOpenAI

real_agent = build_demo_agent(ChatOpenAI(model="gpt-4o-mini"))
print(real_agent.invoke({"input": "How many characters are in 'LangChain'?"}))
```

## Tests

A unit test covers the happy path to ensure the agent executes successfully. Run
all tests with:

```bash
pytest
```
