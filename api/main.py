"""FastAPI application for the Multi-Agent Research Assistant."""

import os
import uuid
import logging
from typing import Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import ValidationError

from schemas import (
    ResearchRequest,
    ResearchResponse,
    ApprovalRequest,
    PDFRequest,
    HealthResponse,
)
from agent.graph import master_graph
from agent.exceptions import APIKeyError, SearchError, LLMError
from utils.pdf_export import generate_pdf
from config import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

thread_states: Dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Multi-Agent Research API")
    yield
    logger.info("Shutting down Multi-Agent Research API")


app = FastAPI(
    title="Multi-Agent Research API",
    description="AI-powered research assistant with multi-agent workflow",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint."""
    return HealthResponse(status="healthy")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@app.post("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest):
    """Start a research task."""
    try:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        logger.info(f"Starting research for topic: {request.topic}")

        for event in master_graph.stream({"topic": request.topic}, config):
            for node_name, node_data in event.items():
                logger.info(f"Completed node: {node_name}")

        state = master_graph.get_state(config)

        thread_states[thread_id] = {
            "topic": request.topic,
            "state": state,
            "config": config,
        }

        return ResearchResponse(
            topic=request.topic,
            status="awaiting_approval",
            analysis=state.values.get("analysis"),
            revision_count=0,
        )

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except APIKeyError as e:
        logger.error(f"API key error: {e}")
        raise HTTPException(status_code=500, detail="API configuration error")
    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/approve", response_model=ResearchResponse)
async def approve_and_write(request: ApprovalRequest):
    """Approve analysis and continue to write the report."""
    if request.thread_id not in thread_states:
        raise HTTPException(status_code=404, detail="Thread not found")

    try:
        thread_data = thread_states[request.thread_id]
        config = thread_data["config"]

        logger.info(f"Continuing research for thread: {request.thread_id}")

        for event in master_graph.stream(None, config):
            for node_name, node_data in event.items():
                logger.info(f"Completed node: {node_name}")

        state = master_graph.get_state(config)

        thread_states[request.thread_id]["state"] = state

        return ResearchResponse(
            topic=state.values.get("topic", ""),
            status="completed" if state.values.get("draft_report") else "in_progress",
            analysis=state.values.get("analysis"),
            draft_report=state.values.get("draft_report"),
            approved=state.values.get("approved", False),
            revision_count=state.values.get("revision_count", 0),
        )

    except Exception as e:
        logger.error(f"Approval flow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pdf")
async def generate_pdf_endpoint(request: PDFRequest):
    """Generate PDF from research report."""
    if request.thread_id not in thread_states:
        raise HTTPException(status_code=404, detail="Thread not found")

    try:
        thread_data = thread_states[request.thread_id]
        state = thread_data["state"]

        if not state.values.get("draft_report"):
            raise HTTPException(status_code=400, detail="No draft report available")

        topic = state.values["topic"]
        draft_report = state.values["draft_report"]
        search_results = state.values.get("search_results", [])

        safe_topic = topic.replace(" ", "_").replace(":", "")
        filename = f"{safe_topic}_Report.pdf"

        generate_pdf(
            topic=topic,
            markdown_content=draft_report,
            search_results=search_results,
            output_filename=filename,
        )

        return FileResponse(
            filename,
            media_type="application/pdf",
            filename=f"{topic}_Report.pdf",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{thread_id}")
async def get_status(thread_id: str):
    """Get the status of a research thread."""
    if thread_id not in thread_states:
        raise HTTPException(status_code=404, detail="Thread not found")

    thread_data = thread_states[thread_id]
    state = thread_data["state"]

    return ResearchResponse(
        topic=state.values.get("topic", ""),
        status="completed" if state.values.get("draft_report") else "in_progress",
        analysis=state.values.get("analysis"),
        draft_report=state.values.get("draft_report"),
        approved=state.values.get("approved", False),
        revision_count=state.values.get("revision_count", 0),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
