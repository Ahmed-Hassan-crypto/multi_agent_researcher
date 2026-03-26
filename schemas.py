"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ResearchRequest(BaseModel):
    """Request model for starting a research task."""

    topic: str = Field(..., min_length=3, max_length=500, description="Research topic")
    max_results: Optional[int] = Field(default=10, ge=1, le=50, description="Maximum search results")

    @field_validator("topic")
    @classmethod
    def topic_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Topic cannot be empty")
        return v


class ResearchResponse(BaseModel):
    """Response model for research status."""

    topic: str
    status: str
    analysis: Optional[str] = None
    draft_report: Optional[str] = None
    approved: Optional[bool] = None
    revision_count: int = 0


class ApprovalRequest(BaseModel):
    """Request model for approving analysis and continuing to writing."""

    thread_id: str = Field(..., min_length=1, description="Thread ID from previous response")


class PDFRequest(BaseModel):
    """Request model for generating PDF."""

    thread_id: str = Field(..., description="Thread ID from previous response")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = "healthy"
    version: str = "1.0.0"
