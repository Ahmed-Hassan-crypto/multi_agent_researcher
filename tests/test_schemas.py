"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from schemas import ResearchRequest, ApprovalRequest, PDFRequest, HealthResponse


class TestResearchRequest:
    """Tests for ResearchRequest schema."""

    def test_valid_topic(self):
        """Test valid topic passes validation."""
        request = ResearchRequest(topic="Artificial Intelligence Trends")
        assert request.topic == "Artificial Intelligence Trends"
        assert request.max_results == 10

    def test_custom_max_results(self):
        """Test custom max_results passes validation."""
        request = ResearchRequest(topic="AI Research", max_results=5)
        assert request.max_results == 5

    def test_topic_too_short(self):
        """Test topic shorter than 3 characters fails."""
        with pytest.raises(ValidationError):
            ResearchRequest(topic="AI")

    def test_topic_too_long(self):
        """Test topic longer than 500 characters fails."""
        with pytest.raises(ValidationError):
            ResearchRequest(topic="A" * 501)

    def test_topic_whitespace_only(self):
        """Test whitespace-only topic fails."""
        with pytest.raises(ValidationError):
            ResearchRequest(topic="   ")

    def test_max_results_minimum(self):
        """Test max_results below minimum fails."""
        with pytest.raises(ValidationError):
            ResearchRequest(topic="Test", max_results=0)

    def test_max_results_maximum(self):
        """Test max_results above maximum fails."""
        with pytest.raises(ValidationError):
            ResearchRequest(topic="Test", max_results=51)


class TestApprovalRequest:
    """Tests for ApprovalRequest schema."""

    def test_valid_thread_id(self):
        """Test valid thread_id passes validation."""
        request = ApprovalRequest(thread_id="abc-123")
        assert request.thread_id == "abc-123"

    def test_empty_thread_id(self):
        """Test empty thread_id fails."""
        with pytest.raises(ValidationError):
            ApprovalRequest(thread_id="")


class TestPDFRequest:
    """Tests for PDFRequest schema."""

    def test_valid_thread_id(self):
        """Test valid thread_id passes validation."""
        request = PDFRequest(thread_id="thread-123")
        assert request.thread_id == "thread-123"


class TestHealthResponse:
    """Tests for HealthResponse schema."""

    def test_default_status(self):
        """Test default status is healthy."""
        response = HealthResponse()
        assert response.status == "healthy"
        assert response.version == "1.0.0"

    def test_custom_status(self):
        """Test custom status."""
        response = HealthResponse(status="unhealthy")
        assert response.status == "unhealthy"
