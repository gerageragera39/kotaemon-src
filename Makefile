.PHONY: install install-gpu run dev

install:
	uv venv .venv --python 3.11
	uv pip install -e ".[dev]"

install-gpu:
	uv venv .venv --python 3.11
	uv pip install -r requirements-gpu.txt
	uv pip install -e ".[dev]"

run:
	.venv/Scripts/python app.py
	# .venv/bin/python app.py      # Linux/Mac

dev:
	.venv/Scripts/python app.py --reload
