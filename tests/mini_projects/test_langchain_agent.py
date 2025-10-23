from mini_projects.langchain_agent.agent_demo import (
    DEFAULT_QUESTION,
    DemoConfig,
    build_demo_agent,
    SimpleToolCallingModel,
    run_demo,
)


def test_run_demo_returns_expected_answer():
    result = run_demo()
    assert result["output"] == "The phrase 'LangChain' has 9 characters."


def test_demo_accepts_custom_llm_and_question():
    llm = SimpleToolCallingModel(response_template="The answer is {count}.")
    config = DemoConfig(question="How many characters are in 'abc'?", llm=llm, verbose=False)
    result = run_demo(config)
    assert result["output"] == "The answer is 3."


def test_build_demo_agent_uses_default_question_when_none_provided():
    agent = build_demo_agent(verbose=False)
    response = agent.invoke({"input": DEFAULT_QUESTION})
    assert response["output"].endswith("has 9 characters.")
