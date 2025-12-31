.PHONY: init format lint test ui api help

help:
	@echo "Available targets:"
	@echo "  init    - Install dependencies and setup pre-commit hooks"
	@echo "  format  - Format code with black and isort"
	@echo "  lint    - Run mypy and pylint"
	@echo "  test    - Run pytest"
	@echo "  ui      - Run Streamlit UI"
	@echo "  api     - Run FastAPI server"

init:
	uv sync --all-groups
	uv run pre-commit install

format:
	uv run black .
	uv run isort .

lint:
	uv run mypy resume_evaluator
	uv run pylint resume_evaluator

test:
	uv run pytest -q

ui:
	uv run streamlit run resume_evaluator/ui/app.py

api:
	uv run uvicorn resume_evaluator.api.app:app --reload
