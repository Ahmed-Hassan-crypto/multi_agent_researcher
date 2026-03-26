import unittest
from unittest.mock import Mock, patch
import os

from agent.state import AgentState


class TestAgentState(unittest.TestCase):
    """Tests for the AgentState TypedDict."""

    def test_agent_state_with_all_fields(self):
        """Test AgentState can be created with all fields."""
        state: AgentState = {
            "topic": "Test Topic",
            "search_results": [{"title": "Result 1", "url": "http://example.com"}],
            "analysis": "Test analysis",
            "draft_report": "Test report",
            "critic_feedback": "Feedback",
            "revision_count": 1,
            "approved": False,
        }
        self.assertEqual(state["topic"], "Test Topic")
        self.assertEqual(len(state["search_results"]), 1)
        self.assertEqual(state["revision_count"], 1)

    def test_agent_state_minimal(self):  # type: ignore[no-unittest-def]
        """Test AgentState with only required fields."""
        state: AgentState = {"topic": "Minimal Topic"}
        self.assertEqual(state["topic"], "Minimal Topic")
        self.assertIsNone(state.get("search_results"))

    def test_agent_state_get_with_defaults(self):  # type: ignore[no-unittest-def]
        """Test getting values with defaults."""
        state: AgentState = {"topic": "Test"}
        self.assertEqual(state.get("search_results", []), [])
        self.assertEqual(state.get("revision_count", 0), 0)


class TestNodesWithMocks(unittest.TestCase):
    """Test agent nodes with mocked external dependencies."""

    @patch("agent.nodes.get_tavily_client")
    def test_research_agent_returns_results(self, mock_get_client):
        """Test research agent returns search results."""
        from agent.nodes import research_agent

        mock_client = Mock()
        mock_client.search.return_value = {
            "results": [
                {"title": "Test Article", "url": "http://test.com", "content": "Test content", "score": 0.9}
            ]
        }
        mock_get_client.return_value = mock_client

        state: AgentState = {"topic": "Test Topic"}
        result = research_agent(state)

        self.assertIn("search_results", result)
        self.assertEqual(len(result["search_results"]), 1)
        self.assertEqual(result["search_results"][0]["title"], "Test Article")
        mock_client.search.assert_called_once_with(
            query="Test Topic", max_results=10, include_answer="advanced", include_raw_content=False
        )

    @patch("agent.nodes.get_tavily_client")
    def test_research_agent_empty_results(self, mock_get_client):
        """Test research agent handles empty results."""
        from agent.nodes import research_agent

        mock_client = Mock()
        mock_client.search.return_value = {"results": []}
        mock_get_client.return_value = mock_client

        state: AgentState = {"topic": "Empty Topic"}
        result = research_agent(state)

        self.assertEqual(result["search_results"], [])

    @patch("agent.nodes.get_gemini_model")
    def test_analysis_agent_returns_outline(self, mock_get_model):
        """Test analysis agent returns structured outline."""
        from agent.nodes import analysis_agent

        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "## Executive Summary\n- Key finding 1"
        mock_llm.invoke.return_value = mock_response
        mock_get_model.return_value = mock_llm

        state: AgentState = {
            "topic": "AI Research",
            "search_results": [{"title": "AI Article", "url": "http://ai.com", "content": "AI content"}],
        }
        result = analysis_agent(state)

        self.assertIn("analysis", result)
        self.assertIn("Executive Summary", result["analysis"])

    @patch("agent.nodes.get_gemini_model")
    def test_writer_agent_returns_draft(self, mock_get_model):
        """Test writer agent returns draft report."""
        from agent.nodes import writer_agent

        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "# AI Research Report\n\nThis is the draft."
        mock_llm.invoke.return_value = mock_response
        mock_get_model.return_value = mock_llm

        state: AgentState = {
            "topic": "AI Research",
            "analysis": "## Outline\n- Section 1",
            "search_results": [{"title": "Source", "url": "http://source.com"}],
            "revision_count": 0,
        }
        result = writer_agent(state)

        self.assertIn("draft_report", result)
        self.assertIn("AI Research Report", result["draft_report"])

    @patch("agent.nodes.get_gemini_model")
    def test_critic_agent_approved(self, mock_get_model):
        """Test critic agent approves good report."""
        from agent.nodes import critic_agent

        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "APPROVED: true\nThe report is comprehensive."
        mock_llm.invoke.return_value = mock_response
        mock_get_model.return_value = mock_llm

        state: AgentState = {"topic": "Test", "draft_report": "Good report", "revision_count": 0}
        result = critic_agent(state)

        self.assertTrue(result.get("approved", False))

    @patch("agent.nodes.get_gemini_model")
    def test_critic_agent_not_approved(self, mock_get_model):
        """Test critic agent rejects poor report."""
        from agent.nodes import critic_agent

        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "APPROVED: false\nNeeds more detail."
        mock_llm.invoke.return_value = mock_response
        mock_get_model.return_value = mock_llm

        state: AgentState = {"topic": "Test", "draft_report": "Short", "revision_count": 0}
        result = critic_agent(state)

        self.assertFalse(result.get("approved", True))
        self.assertIn("critic_feedback", result)

    @patch("agent.nodes.get_gemini_model")
    def test_critic_agent_max_revisions(self, mock_get_model):
        """Test critic agent approves after max revisions."""
        from agent.nodes import critic_agent

        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "APPROVED: false\nStill needs work."
        mock_llm.invoke.return_value = mock_response
        mock_get_model.return_value = mock_llm

        state: AgentState = {"topic": "Test", "draft_report": "Report", "revision_count": 3}
        result = critic_agent(state)

        self.assertTrue(result.get("approved", False))


class TestNodesErrorHandling(unittest.TestCase):
    """Test error handling in agent nodes."""

    def test_research_agent_missing_api_key(self):
        """Test research agent raises error without API key."""
        from agent.nodes import research_agent

        with patch.dict(os.environ, {}, clear=True):
            with patch("agent.nodes.get_tavily_client", side_effect=ValueError("TAVILY_API_KEY not set")):
                with self.assertRaises(ValueError) as context:
                    research_agent({"topic": "Test"})
                self.assertIn("TAVILY_API_KEY", str(context.exception))

    def test_analysis_agent_missing_api_key(self):
        """Test analysis agent raises error without API key."""
        from agent.nodes import analysis_agent

        with patch.dict(os.environ, {}, clear=True):
            with patch("agent.nodes.get_gemini_model", side_effect=ValueError("GEMINI_API_KEY not set")):
                with self.assertRaises(ValueError) as context:
                    analysis_agent({"topic": "Test", "search_results": []})
                self.assertIn("GEMINI_API_KEY", str(context.exception))


if __name__ == "__main__":
    unittest.main()
