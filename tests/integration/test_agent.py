
import asyncio
import pytest
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from app.agent import root_agent


@pytest.mark.asyncio
async def test_agent_initialization():
    """Tests that the root_agent is an instance of Agent."""
    assert isinstance(root_agent, Agent)

@pytest.mark.asyncio
async def test_agent_responds_to_hello():
    """Tests that the agent can respond to a simple 'hello' message."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="test_app", user_id="test_user", session_id="test_session"
    )
    runner = Runner(
        agent=root_agent, app_name="test_app", session_service=session_service
    )
    query = "hello"
    response_text = ""
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            break  # Exit after getting the final response

    assert response_text is not None
    assert len(response_text) > 0
    print(f"Agent response: {response_text}")
