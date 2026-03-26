import unittest
from unittest.mock import Mock, patch

from agent.state import AgentState
from agent.graph import master_graph, should_continue_revisions


class TestGraph(unittest.TestCase):
    """Tests for LangGraph workflow."""

    def test_should_continue_revisions_approved(self):
        """Test revision continues when not approved."""
        state: AgentState = {"topic": "Test", "approved": False, "revision_count": 1}
        result = should_continue_revisions(state)
        self.assertEqual(result, "continue")

    def test_should_continue_revisions_not_approved(self):
        """Test revision stops when approved."""
        state: AgentState = {"topic": "Test", "approved": True, "revision_count": 0}
        result = should_continue_revisions(state)
        self.assertEqual(result, "end")

    def test_should_continue_revisions_max_count(self):
        """Test revision stops at max count."""
        state: AgentState = {"topic": "Test", "approved": False, "revision_count": 3}
        result = should_continue_revisions(state)
        self.assertEqual(result, "end")

    def test_should_continue_revisions_default_approved(self):
        """Test defaults to continue when approved not set."""
        state: AgentState = {"topic": "Test", "revision_count": 0}
        result = should_continue_revisions(state)
        self.assertEqual(result, "continue")

    def test_graph_compiles(self):
        """Test that the graph compiles without errors."""
        self.assertIsNotNone(master_graph)
        self.assertTrue(hasattr(master_graph, "stream"))
        self.assertTrue(hasattr(master_graph, "get_state"))


class TestGraphNodesIntegration(unittest.TestCase):
    """Integration tests for graph nodes."""

    @patch("agent.nodes.get_tavily_client")
    @patch("agent.nodes.get_llm")
    def test_research_to_analysis_flow(self, mock_llm, mock_tavily):
        """Test research node output flows to analysis node."""
        from agent.nodes import research_agent, analysis_agent

        mock_tavily_client = Mock()
        mock_tavily_client.search.return_value = {
            "results": [{"title": "Test", "url": "http://test.com", "content": "Content", "score": 0.9}]
        }
        mock_tavily.return_value = mock_tavily_client

        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "# Analysis"
        mock_llm.invoke.return_value = mock_response
        mock_llm.return_value = mock_llm

        state: AgentState = {"topic": "Test Topic"}
        research_result = research_agent(state)

        self.assertIn("search_results", research_result)

        analysis_state: AgentState = {**research_result, "topic": "Test Topic"}
        analysis_result = analysis_agent(analysis_state)

        self.assertIn("analysis", analysis_result)


if __name__ == "__main__":
    unittest.main()
