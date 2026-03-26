# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Unix/Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the Streamlit application
streamlit run app.py
```

### Testing
```bash
# Test with a sample topic
# In the Streamlit UI, enter: "Recent Advancements in Solid State Batteries"
# Verify the analysis pause and approval flow works
# Verify PDF download generates correctly
```

## Code Architecture

### High-Level Structure
```
multi_agent_researcher/
├── agent/              # LangGraph agent ecosystem (IMPLEMENTED)
│   ├── state.py        # AgentState TypedDict schema
│   ├── nodes.py        # 4 agent nodes: research, analysis, writer, critic
│   └── graph.py        # StateGraph with routing and human approval pause
├── utils/
│   └── pdf_export.py   # fpdf2-based PDF report generator
├── app.py              # Streamlit UI with approval button and PDF download
├── requirements.txt    # Python dependencies
└── implementation_plan.md
```

### Component Responsibilities

**Agent System (LangGraph):**
- `state.py`: Defines `AgentState` with fields: `topic`, `search_results`, `analysis`, `draft_report`, `critic_feedback`, `revision_count`
- `nodes.py`: Implements 4 agents:
  - `research_agent`: Uses Tavily API for web data retrieval
  - `analysis_agent`: Uses Gemini to synthesize findings into outline
  - `writer_agent`: Uses Gemini to draft full markdown report
  - `critic_agent`: Reviews against quality heuristics, routes back for revision if needed
- `graph.py`: Wires the flow: `research` → `analysis` → `human_approval` → `writer` ↔ `critic` → END
  - Uses `interrupt_before=["writer_agent"]` for human-in-the-loop approval
  - Uses `MemorySaver()` for checkpoint persistence

**PDF Export (fpdf2):**
- Converts markdown report to formatted PDF
- Injects topic name, current date, and citations from Tavily results
- Pure Python implementation (no external system dependencies)

**Frontend (Streamlit):**
- `app.py`: Interactive research interface
  - Topic input field
  - Real-time agent state display during execution
  - "Approve & Write" button after analysis phase
  - "Download Report (PDF)" button for final output

### Data Flow
1. User enters research topic → Streamlit submits to LangGraph
2. Research agent queries Tavily API → stores raw search results
3. Analysis agent synthesizes findings → creates outline
4. Graph pauses for human approval (LangGraph `interrupt_before`)
5. User clicks "Approve & Write" → writer agent drafts report
6. Critic agent reviews → loops back if quality fails heuristics
7. Final report exported as PDF via fpdf2

### Key Technical Details
- Search API: Tavily (configured via `TAVILY_API_KEY` in `.env`)
- LLM: Google Gemini 2.5 Flash (temperature 0.0 for deterministic outputs)
- Vector Store: Not used - direct search results stored in state
- Human-in-the-loop: LangGraph `interrupt_before` + `MemorySaver` for pause/resume
- PDF: fpdf2 for pure Python PDF generation without external dependencies
- Prompt Engineering: Quality heuristics in critic prompt enforce revision cycles
