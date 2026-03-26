"""Custom exceptions for the multi-agent research system."""


class ResearchAssistantError(Exception):
    """Base exception for all research assistant errors."""

    pass


class APIKeyError(ResearchAssistantError):
    """Raised when required API key is missing."""

    pass


class SearchError(ResearchAssistantError):
    """Raised when search operation fails."""

    pass


class LLMError(ResearchAssistantError):
    """Raised when LLM operation fails."""

    pass


class PDFGenerationError(ResearchAssistantError):
    """Raised when PDF generation fails."""

    pass


class GraphExecutionError(ResearchAssistantError):
    """Raised when graph execution fails."""

    pass


class ValidationError(ResearchAssistantError):
    """Raised when input validation fails."""

    pass
