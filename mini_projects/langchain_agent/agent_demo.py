"""Self-contained LangChain agent demo used for classroom presentations."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict, List, Optional, Sequence, Union

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain.tools import tool
from langchain.tools.base import BaseTool
from pydantic import ConfigDict, PrivateAttr

DEFAULT_QUESTION = "How many characters are in 'LangChain'?"


@tool
def character_count(text: str) -> int:
    """Count the number of characters in the provided text."""

    return len(text)


@dataclass
class DemoConfig:
    """Configuration for the agent demo."""

    question: str = DEFAULT_QUESTION
    llm: Optional[BaseLanguageModel] = None
    verbose: bool = True


class SimpleToolCallingModel(BaseChatModel):
    """A tiny deterministic chat model that always calls the counting tool.

    The model is intentionally basic: it looks for quoted text in the latest
    human message, issues a tool call for that text, and then builds a short
    natural language response once the tool result is available.  This keeps the
    demo fully offline while still exercising LangChain's agent runtime.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    response_template: str = "The phrase '{text}' has {count} characters."
    _last_text: str = PrivateAttr(default="")
    _tool_name: str = PrivateAttr(default="character_count")
    _tool_call_id: str = PrivateAttr(default="tool_call_0")

    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], type, BaseTool]],
        *,
        tool_choice: Optional[Union[str]] = None,
        **_: Any,
    ) -> Runnable[BaseMessage, BaseMessage]:
        if not tools:
            raise ValueError("At least one tool is required for this demo model.")

        first = tools[0]
        if isinstance(first, BaseTool):
            self._tool_name = first.name
        elif isinstance(first, dict):
            self._tool_name = first.get("name", self._tool_name)
        else:
            self._tool_name = getattr(first, "name", self._tool_name)

        if tool_choice not in (None, "any", self._tool_name):
            raise ValueError(f"Unsupported tool choice: {tool_choice!r}")

        return self

    def _call_tool(self, text: str) -> AIMessage:
        self._last_text = text
        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": self._tool_name,
                    "args": {"text": text},
                    "id": self._tool_call_id,
                    "type": "tool_call",
                }
            ],
        )

    def _final_response(self, tool_message: ToolMessage) -> AIMessage:
        count = tool_message.content
        if isinstance(count, list):
            count = " ".join(map(str, count))
        count = str(count).strip()
        text = self._last_text or "the provided text"
        return AIMessage(content=self.response_template.format(text=text, count=count))

    def _extract_text(self, user_message: BaseMessage) -> str:
        match = re.search(r"'([^']+)'", user_message.content)
        if match:
            return match.group(1)
        match = re.search(r'"([^"]+)"', user_message.content)
        if match:
            return match.group(1)
        return user_message.content.strip()

    def _generate(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any
    ) -> ChatResult:
        del stop, kwargs
        latest = messages[-1] if messages else None
        if isinstance(latest, ToolMessage):
            message = self._final_response(latest)
        else:
            human_messages = [m for m in messages if m.type == "human"]
            if not human_messages:
                raise ValueError("The demo model expects at least one human message.")
            text = self._extract_text(human_messages[-1])
            message = self._call_tool(text)
        return ChatResult(generations=[ChatGeneration(message=message)])

    @property
    def _llm_type(self) -> str:
        return "simple-tool-calling-model"


def build_demo_agent(llm: Optional[BaseLanguageModel] = None, *, verbose: bool = True) -> AgentExecutor:
    """Create an agent executor ready to answer the demo question."""

    tools = [character_count]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. "
                "If the user asks for the length of a string you must use the available tools.",
            ),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    if llm is None:
        llm = SimpleToolCallingModel()

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=verbose)


def run_demo(config: Optional[DemoConfig] = None) -> Dict[str, str]:
    """Run the default demonstration question through the agent.

    Parameters
    ----------
    config:
        Optional configuration that lets callers override the default
        question, language model, or verbosity.
    """

    config = config or DemoConfig()
    agent_executor = build_demo_agent(config.llm, verbose=config.verbose)
    return agent_executor.invoke({"input": config.question})


if __name__ == "__main__":
    result = run_demo()
    print("\nFinal answer:\n", result["output"], sep="")
