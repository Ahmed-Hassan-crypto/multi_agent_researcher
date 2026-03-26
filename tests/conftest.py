"""Pytest configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock, patch


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_tavily_client():
    """Mock Tavily client for testing."""
    with patch("agent.nodes.get_tavily_client") as mock:
        client = Mock()
        client.search.return_value = {
            "results": [
                {"title": "Test Article", "url": "http://test.com", "content": "Test content", "score": 0.9}
            ]
        }
        mock.return_value = client
        yield client


@pytest.fixture
def mock_gemini_model():
    """Mock Gemini model for testing."""
    with patch("agent.nodes.get_gemini_model") as mock:
        llm = Mock()
        response = Mock()
        response.content = "Mock response content"
        llm.invoke.return_value = response
        mock.return_value = llm
        yield llm


@pytest.fixture
def sample_agent_state():
    """Sample AgentState for testing."""
    return {
        "topic": "Test Topic",
        "search_results": [
            {"title": "Source 1", "url": "http://source1.com", "content": "Content 1", "score": 0.9}
        ],
        "analysis": "# Analysis\n- Point 1\n- Point 2",
        "draft_report": "# Report\n\nThis is a test report.",
        "critic_feedback": "",
        "revision_count": 0,
        "approved": False,
    }
