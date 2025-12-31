# Resume Evaluator

A comprehensive resume evaluation system that uses OpenAI LLM, LangGraph, FastAPI, and Streamlit to evaluate candidate resumes against job descriptions.

## Features

- **Structured Data Extraction**: Uses OpenAI LLM with Pydantic validation to extract structured candidate profiles and job descriptions
- **Fit Evaluation**: Comprehensive evaluation with fit scores, strengths, gaps, and recommendations
- **Multiple Interfaces**: 
  - FastAPI REST API for programmatic access
  - Streamlit UI for interactive evaluation
  - Jupyter notebook examples for experimentation
- **Robust Pipeline**: LangGraph-based workflow with error handling and retries
- **Quality Assurance**: Pre-commit hooks, type checking, and linting


## Quickstart

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. **Install dependencies and setup pre-commit hooks:**

```bash
make init
```

Or manually:

```bash
uv sync --all-groups
uv run pre-commit install
```

2. **Configure environment variables:**

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### Running the Application

#### Streamlit UI

```bash
make ui
```

Or:

```bash
uv run streamlit run resume_evaluator/ui/app.py
```

Then open your browser to the URL shown (typically http://localhost:8501).

#### FastAPI Server

```bash
make api
```

Or:

```bash
uv run uvicorn resume_evaluator.api.app:app --reload
```

The API will be available at http://localhost:8000.

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

#### Example Notebook

The example notebook is available as both `.py` and `.ipynb` (via Jupytext):

```bash
# Run as Python script
uv run python examples/quickstart.py

# Or open in Jupyter
uv run jupyter notebook examples/quickstart.ipynb
```

## API Usage

### POST /evaluate (multipart/form-data)

```bash
curl -X POST "http://localhost:8000/evaluate" \
  -F "resume=@resume.pdf" \
  -F "job_description=Looking for a senior software engineer..."
```

### POST /evaluate/json

```bash
curl -X POST "http://localhost:8000/evaluate/json" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "John Doe\nSoftware Engineer...",
    "job_description_text": "Looking for a senior software engineer..."
  }'
```

### Response Format

```json
{
  "candidate_profile": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "summary": "...",
    "skills_primary": ["Python", "FastAPI"],
    ...
  },
  "job_description": {
    "title": "Senior Software Engineer",
    "summary": "...",
    "required_skills": ["Python", "FastAPI"],
    ...
  },
  "evaluation": {
    "fit_score": 75,
    "is_fit": true,
    "fit_summary": "...",
    "strengths": [...],
    "gaps": [...],
    "recommendations": [...],
    "missing_keywords": [...],
    "risk_flags": [...]
  }
}
```

## Development

### Pre-commit Hooks

Pre-commit hooks are automatically installed with `make init`. They run:

- Code formatting (black, isort)
- Linting (mypy, pylint)
- File checks (JSON, YAML, TOML validation)
- Notebook management (jupytext sync, nbstripout)
- Security checks (private key detection)

### Adding Dependencies

Add runtime dependencies to `pyproject.toml` under `[project.dependencies]`.

Add dev dependencies to `[project.optional-dependencies.dev]`.

Then run:

```bash
uv sync --all-groups
```

### Type Checking

The project uses strict mypy configuration. Type hints are required for all functions.

### Code Style

- Line length: 100 characters
- Formatter: black
- Import sorter: isort (black-compatible profile)

## Architecture

### Pipeline Flow

1. **Parse Resume**: Extract text from PDF (if needed)
2. **Extract Profile**: Use LLM to structure candidate information
3. **Extract Job Description**: Use LLM to structure job requirements
4. **Evaluate Fit**: Use LLM to assess fit and generate evaluation

### LLM Integration

- Uses OpenAI Chat Completions API with `response_format={"type": "json_object"}`
- Includes Pydantic JSON schema in prompts for structure enforcement
- Validates all responses with Pydantic models
- Retries on transient errors using tenacity
- Temperature set to 0.2 for consistent outputs


## Contributing

1. Ensure pre-commit hooks pass
2. Run tests: `make test`
3. Format code: `make format`
4. Lint code: `make lint`
