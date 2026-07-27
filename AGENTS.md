# AGENTS.md — Dev Guide for research-agent

## Project Overview
Knowledge-graph-powered research paper analysis agent.
- **LangGraph** for workflow orchestration (ingestion, explanation, comparison)
- **Kuzu** for lightweight embedded knowledge graph
- **Milvus** for semantic vector search (with etcd + minio via docker-compose)
- **Gradio** for web UI
- **marker-pdf** for PDF → Markdown extraction
- **vLLM** / OpenAI-compatible API for LLM inference

## Structure
```
src/research_agent/
├── cli.py              # CLI entry (optional batch operations)
├── config.py           # Pydantic-settings config
├── models/             # Pydantic schemas
├── graphs/             # LangGraph state machines
├── nodes/              # Shared node callables
├── storage/            # DB layer (SQLite, Milvus, Kuzu)
└── ui/                 # Gradio app
tests/
notebooks/
```

## Environment
- Conda env name: `research_venv` (Python 3.12)
- Temp files directory: `.tmp/` (ignored by git and docker)

## Setup
```bash
# Activate conda environment
conda activate research_venv

# Install in editable mode
pip install -e ".[dev]"

# Copy environment config
cp .env.example .env
# Edit .env with your vLLM endpoint
```

## Docker (Milvus + App)
```bash
# Start Milvus infrastructure and app
docker-compose up -d

# Milvus standalone: http://localhost:19530
# MinIO: http://localhost:9001
# Gradio app: http://localhost:7860
```

## Running the App
```bash
# CLI (batch ingest)
python -m research_agent.cli ingest --pdf path/to/paper.pdf --collection "transformers"

# Gradio UI
python -m research_agent.ui.gradio_app
```

## LangGraph Design Patterns
- Graphs are defined in `graphs/` as `StateGraph` instances building functions
- Nodes are pure callables: `def node(state: State) -> dict:` returning state updates
- Conditional edges return string routing keys for loop control
- Ingestion graph includes a **refinement loop**: extraction → quality check → (refine or store)
- Knowledge graph is always queried for explain and compare operations (not optional)

## Testing
```bash
pytest tests/
```

## Lint / Format
```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```
