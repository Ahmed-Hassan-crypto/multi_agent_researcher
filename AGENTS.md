# AGENTS.md - Agentic Coding Guidelines

## Project Overview
- **Type**: Python/Streamlit multi-agent research assistant
- **Structure**: Main app in `app.py`, agent system in `agent/`, utilities in `utils/`, tests in `tests/`
- **Dependencies**: streamlit, langgraph, langchain-google-genai, tavily-python, python-dotenv, fpdf2, markdown

## Build / Run Commands

### Environment Setup
```bash
cd multi_agent_researcher
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Unix/Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### Running the Application
```bash
# Start main Streamlit app
streamlit run app.py
```

### Running Tests
```bash
# Run all tests with pytest
pytest

# Run tests with coverage
pytest --cov=agent --cov=utils --cov-report=html

# Run a specific test file
pytest tests/test_agent_state.py

# Run tests matching a pattern
pytest -k "test_research"

# Run with verbose output
pytest -v
```

### Code Quality Tools
```bash
# Linting with ruff
ruff check .

# Type checking with mypy
mypy agent/ utils/ --ignore-missing-imports

# Format code
ruff format .
```

---

## Code Style Guidelines

### Imports
- Standard library first, then third-party, then local
- Group imports with blank lines between groups
- Use absolute imports: `from agent.graph import master_graph`
- Avoid wildcard imports (`from X import *`)

### Formatting
- Maximum line length: 100 characters (soft limit 120)
- Use 4 spaces for indentation (not tabs)
- No trailing whitespace

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Variables/functions | snake_case | `topic`, `generate_pdf` |
| Classes | PascalCase | `GameConfig`, `PDF` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Module files | snake_case | `pdf_export.py` |

### Type Hints
- Use type hints for all function arguments and return types
- Use `typing` module for complex types
```python
def generate_pdf(topic: str, markdown_content: str, search_results: list, output_filename: str = "report.pdf") -> str:
```

### Classes
- Use dataclasses or TypedDict for simple data containers
- Document public methods with docstrings

### Error Handling
- Use custom exceptions from `agent/exceptions.py`
- Include meaningful error messages
- Log errors before raising
```python
try:
    client.search(query)
except Exception as e:
    logger.error(f"Search failed: {e}")
    raise SearchError(f"Search failed: {e}") from e
```

---

## Project-Specific Patterns

### Streamlit Apps
- Use `st.session_state` for persistent state
- Call `st.set_page_config()` at the start
- Use `st.rerun()` to refresh after state changes

### LangGraph Integration
- Define agent state using `TypedDict` in `agent/state.py`
- Use `MemorySaver()` for checkpoint persistence
- Use `interrupt_before` for human-in-the-loop pauses
- Configuration passed via `config = {"configurable": {"thread_id": "..."}}`

### PDF Generation (fpdf2)
- Sanitize unicode text before rendering
- Handle HTML rendering failures gracefully

### Testing
- Use pytest with mocks for external APIs
- Create fixtures in `tests/conftest.py`
- Test error handling paths

---

## File Structure
```
multi_agent_researcher/
├── app.py                    # Main Streamlit app
├── config.py                 # Logging configuration
├── agent/
│   ├── __init__.py
│   ├── config.py             # App configuration
│   ├── exceptions.py         # Custom exceptions
│   ├── state.py              # AgentState TypedDict
│   ├── nodes.py              # 4 agent implementations
│   └── graph.py              # LangGraph StateGraph
├── utils/
│   ├── __init__.py
│   └── pdf_export.py         # PDF generation
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_agent_state.py   # Agent tests
│   ├── test_graph.py         # Graph tests
│   └── test_pdf_export.py    # PDF tests
├── .github/workflows/
│   └── ci.yml                # GitHub Actions CI
├── pytest.ini
├── requirements.txt
├── .env.example
└── .env
```

---

## Environment Variables
Create a `.env` file (see `.env.example`):
```
TAVILY_API_KEY=your_api_key_here
GEMINI_API_KEY=your_api_key_here
```

---

## Common Tasks

### Adding a New Agent Node
1. Add function to `agent/nodes.py`
2. Add logging and error handling
3. Register in `agent/graph.py`
4. Add tests in `tests/`

### Running the App in Development
1. Ensure virtual environment is activated
2. Run `streamlit run app.py`
3. Open browser at `http://localhost:8501`

### CI/CD
- GitHub Actions workflow in `.github/workflows/ci.yml`
- Runs: linting, type checking, tests with coverage
- Requires secrets: TAVILY_API_KEY, GEMINI_API_KEY
