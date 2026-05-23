Luca's dataset is in `.\dataset\documents`

Upload `.\dataset\testing_files` in your system!

`rag_eval_dataset.json` is a file with simple questions for files in `.\dataset\testing_files`

## Docker (Python 3.11)

The container image uses **Python 3.11** and installs dependencies from `requirements_gerageragera39.txt`, matching a local `pip install -r requirements_gerageragera39.txt` setup.

**Prerequisites:** Docker Desktop (or Docker Engine) running, with BuildKit enabled (default in recent Docker versions).

### Build images

Three build targets are available:

| Target | Description |
|--------|-------------|
| `lite` | Core app and pinned requirements |
| `full` | Adds OCR, LibreOffice, PyTorch, and document-processing stack |
| `ollama` | `full` plus Ollama and `nomic-embed-text` embedding model |

```bash
# Minimal image
docker build --target lite -t kotaemon:lite .

# Recommended for document RAG (OCR, unstructured, torch)
docker build --target full -t kotaemon:full .

# Includes Ollama for local embeddings/models
docker build --target ollama -t kotaemon:ollama .
```

On **Linux amd64** with an NVIDIA GPU, you can pass a CUDA PyTorch index (optional):

```bash
docker build --target full \
  --build-arg TORCH_INDEX_URL=https://download.pytorch.org/whl/cu121 \
  -t kotaemon:full .
```

Use a different requirements file (optional):

```bash
docker build --target lite \
  --build-arg REQUIREMENTS_FILE=requirements_gerageragera39.txt \
  -t kotaemon:lite .
```

### Run the app

Create a `.env` file in the project root (copy from `.env.example`) before running, or mount your own env file.

```bash
# Persist app data on the host
docker run --rm -p 7860:7860 \
  -v "%cd%\ktem_app_data:/app/ktem_app_data" \
  --env-file .env \
  kotaemon:full

docker run --rm -p 7860:7860 `
  -v "${PWD}\ktem_app_data:/app/ktem_app_data" `
  --env-file .env `
  kotaemon:full
```

On Linux/macOS, replace `%cd%` with `$(pwd)`:

```bash
docker run --rm -p 7860:7860 \
  -v "$(pwd)/ktem_app_data:/app/ktem_app_data" \
  --env-file .env \
  kotaemon:full
```

Open **http://localhost:7860** in your browser.

### Demo / SSO modes

```bash
docker run --rm -p 7860:7860 -e KH_DEMO_MODE=true kotaemon:lite
docker run --rm -p 7860:7860 -e KH_SSO_ENABLED=true --env-file .env kotaemon:lite
```

### Local install (without Docker)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements_gerageragera39.txt
pip install -e .
python app.py
```

Python **3.11** is required (`requires-python >= 3.11` in `pyproject.toml`).
