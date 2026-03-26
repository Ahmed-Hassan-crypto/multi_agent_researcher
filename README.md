# 🤖 Multi-Agent Research Assistant

An AI-powered research assistant that uses LangGraph to orchestrate multiple AI agents for comprehensive research and report generation.

![Python](https://img.shields.io/badge/python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.40+-red)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **Multi-Agent System**: Research, Analysis, Writing, and Review agents
- **Human-in-the-Loop**: Approve analysis before report generation
- **Web Search**: Tavily API for real-time information
- **AI Writing**: Qwen2.5:4b (local, free via Ollama)
- **PDF Export**: Download professional PDF reports
- **Production-Ready**: Docker, CI/CD, testing, type hints

## 🛠️ Quick Start (Local)

### Prerequisites

1. **Install Ollama** (free, local AI):
   - Download from https://ollama.com
   - Run: `ollama serve`

2. **Download the model**:
   ```bash
   ollama pull qwen3.5:4b
   ```

### Run the App

```bash
# Clone the project
cd multi_agent_researcher

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Or (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (only Tavily needed for search)
echo "TAVILY_API_KEY=your_key" > .env
# Get free key at https://tavily.com

# Run the app
streamlit run app.py
```

Open http://localhost:8501

## 📖 Usage

1. **Enter a research topic** in the text field
2. Click **Start Research** - agents will gather and analyze information
3. **Review the analysis outline** when ready
4. Click **Approve & Write Report** to generate the full report
5. **Download PDF** when complete

## 🏗️ Project Structure

```
multi_agent_researcher/
├── app.py                 # Streamlit UI
├── agent/                 # LangGraph agents
│   ├── nodes.py          # Agent implementations (Ollama)
│   └── graph.py          # Workflow definition
├── utils/                # Utilities
│   └── pdf_export.py     # PDF generation
├── tests/                # Test suite
├── Dockerfile            # Container build
└── requirements.txt      # Dependencies
```

## 🔧 Development

```bash
# Run tests
pytest tests/ -v --cov=agent --cov=utils

# Run linting
ruff check .
```

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome!
