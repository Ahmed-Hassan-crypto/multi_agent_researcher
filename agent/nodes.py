import os
import logging

from tavily import TavilyClient

from .state import AgentState
from .exceptions import APIKeyError, SearchError, LLMError

logger = logging.getLogger(__name__)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:4b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"


def get_tavily_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.error("TAVILY_API_KEY not found in environment")
        raise APIKeyError("TAVILY_API_KEY not set in environment")
    return TavilyClient(api_key=api_key)


def get_llm():
    """Get LLM - uses Groq for cloud, Ollama for local."""
    if USE_GROQ:
        return get_groq_model()
    return get_ollama_model()


def get_ollama_model():
    """Get Ollama model (local, free)."""
    try:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=OLLAMA_MODEL,
            temperature=0.0,
            base_url=OLLAMA_BASE_URL
        )
    except Exception as e:
        logger.error(f"Failed to initialize Ollama: {e}")
        raise LLMError(f"Ollama not available: {e}. Install from https://ollama.com") from e


def get_groq_model():
    """Get Groq model (free tier, for cloud deployment)."""
    try:
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise APIKeyError("GROQ_API_KEY not set. Get free key at https://console.groq.com")
        return ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0.0,
            api_key=api_key
        )
    except Exception as e:
        logger.error(f"Failed to initialize Groq: {e}")
        raise LLMError(f"Groq initialization failed: {e}") from e


def ensure_ollama():
    """Ensure Ollama is running (for local use only)."""
    try:
        get_llm()
    except Exception:
        logger.warning("Ollama not available. Install from https://ollama.com")


def research_agent(state: AgentState) -> AgentState:
    topic = state["topic"]
    logger.info(f"Starting research for topic: {topic}")
    try:
        client = get_tavily_client()
        search_results = client.search(
            query=topic,
            max_results=10,
            include_answer="advanced",
            include_raw_content=False
        )
        results = []
        for item in search_results.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "score": item.get("score", 0.0)
            })
        logger.info(f"Research completed, found {len(results)} results")
        return {"topic": topic, "search_results": results}  # type: ignore[return-value]
    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise SearchError(f"Search failed: {e}") from e


def analysis_agent(state: AgentState) -> AgentState:
    topic = state["topic"]
    search_results = state.get("search_results", [])
    logger.info(f"Starting analysis for topic: {topic}")
    
    try:
        llm = get_llm()
        
        results_summary = "\n\n".join([
            f"Source {i+1}: {r.get('title', 'N/A')}\n{r.get('content', 'N/A')}"
            for i, r in enumerate(search_results[:5])
        ])
        
        prompt = f"""You are a research analyst. Given the topic "{topic}" and search results, 
create a structured outline for a comprehensive research report.

Search Results:
{results_summary}

Provide a detailed outline with:
1. Executive Summary
2. Key Findings (3-5 main points)
3. Supporting Evidence for each finding
4. Conclusion
5. References

Be specific and actionable."""
        
        response = llm.invoke(prompt)
        analysis = response.content if hasattr(response, "content") else str(response)
        logger.info("Analysis completed successfully")
        return {"topic": topic, "analysis": analysis}  # type: ignore[return-value]
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise LLMError(f"Analysis failed: {e}") from e


def writer_agent(state: AgentState) -> AgentState:
    topic = state["topic"]
    analysis = state.get("analysis", "")
    search_results = state.get("search_results", [])
    revision_count = state.get("revision_count", 0)
    
    logger.info(f"Starting report writing for topic: {topic} (revision {revision_count})")
    
    try:
        llm = get_llm()
        
        citations = "\n".join([
            f"[{i+1}] {r.get('title', 'N/A')}: {r.get('url', 'N/A')}"
            for i, r in enumerate(search_results[:10])
        ])
        
        prompt = f"""You are a professional technical writer. Write a comprehensive research report 
on the topic: "{topic}"

Based on this outline:
{analysis}

Requirements:
- Write in a professional, academic tone
- Include proper sections with headings
- Cite sources using numbered references
- Make it comprehensive (2000-3000 words)
- Include an abstract and conclusion

Citations:
{citations}

Write the full report in markdown format."""
        
        response = llm.invoke(prompt)
        draft_report = response.content if hasattr(response, "content") else str(response)
        logger.info("Report drafting completed")
        revision_count = state.get("revision_count", 0)
        return {"topic": topic, "draft_report": draft_report, "revision_count": revision_count}  # type: ignore[return-value]
    except Exception as e:
        logger.error(f"Writing failed: {e}")
        raise LLMError(f"Writing failed: {e}") from e


def critic_agent(state: AgentState) -> AgentState:
    draft_report = state.get("draft_report", "")
    topic = state["topic"]
    revision_count = state.get("revision_count", 0)
    
    llm = get_llm()
    
    prompt = f"""You are a critical reviewer. Evaluate this research report on "{topic}" 
    for quality, accuracy, and completeness.

    Report:
    {draft_report}

    Evaluate against these criteria:
    1. Relevance - Does it address the topic comprehensively?
    2. Structure - Is it well-organized with clear sections?
    3. Clarity - Is it written clearly without jargon?
    4. Citations - Are sources properly cited?
    5. Length - Is it substantial (at least 1500 words)?

    Provide feedback in this format:
    APPROVED: [true/false]
    FEEDBACK: [Specific suggestions for improvement if not approved]
    """
    
    response = llm.invoke(prompt)
    feedback_text = response.content if hasattr(response, "content") else str(response)
    
    approved = "APPROVED: TRUE" in feedback_text.upper()
    feedback = feedback_text if not approved else ""
    
    if not approved and revision_count < 3:
        return {
            "topic": topic,
            "draft_report": draft_report,
            "critic_feedback": feedback,
            "revision_count": revision_count + 1,
            "approved": False
        }
    else:
        return {"topic": topic, "draft_report": draft_report, "critic_feedback": feedback, "approved": True}
