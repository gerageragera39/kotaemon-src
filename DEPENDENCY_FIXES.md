# Dependency installation fixes for Windows / Python 3.11

This file records the resolver/runtime fixes applied while installing the project into:

`C:\Users\SED\Documents\new_my_ktmon\test5\.venv`

## Verified environment

- Python: `3.11.9`
- GPU: `NVIDIA GeForce RTX 4090 Laptop GPU`
- CUDA wheel runtime: `12.1`
- Project install: `uv pip install -e .`
- Final resolver check: `uv pip check` → all compatible

## Fixes applied

### 1. Adobe PDF Services SDK moved out of base install

`pdfservices-sdk==2.3.1` requires `urllib3<1.27`, while Gradio 4.x requires `urllib3>=2`.

Action:

- Removed `pdfservices-sdk` from base `pyproject.toml` / `requirements.txt`.
- Added `requirements-adobe.txt` and optional `adobe` extra for isolated/manual Adobe testing.

### 2. Microsoft GraphRAG moved out of base install

`graphrag<=0.3.6` requires `aiofiles>=24.1`, while Gradio 4.x requires `aiofiles<24`.

Action:

- Removed `graphrag` from base install.
- Added `requirements-graphrag.txt` and optional `ms-graphrag` extra.
- Changed `USE_MS_GRAPHRAG` default to `False` in `flowsettings.py`.

### 3. `unstructured[all-docs]` relaxed

Old `<0.16` versions pulled `pycrypto` through `layoutparser/pdfplumber`, which fails to build on Windows/Python 3.11.

Action:

- Changed `unstructured[all-docs]>=0.15.8,<0.16` to `unstructured[all-docs]>=0.16.0`.

### 4. `duckduckgo-search` pinned below 6

`duckduckgo-search 6.1.x` pulls `pyreqwest-impersonate`, which tried to build Rust/MSVC native code and failed without `link.exe`.

Action:

- Changed to `duckduckgo-search>=5.3.1,<6`.

### 5. LangChain pinned to compatible legacy API family

The source imports legacy modules such as:

- `langchain.schema`
- `langchain.agents.initialize_agent`
- `langchain.text_splitter`

These are not available in LangChain 1.x.

Action:

- Pinned LangChain packages to 0.2/0.1 compatible family.
- Removed orphan LangChain 1.x packages from `.venv`: `langgraph*`, `langchain-classic`.

### 6. CUDA PyTorch pinned explicitly

A generic reinstall kept CPU torch and changed `numpy`, `pillow`, and `markupsafe` to incompatible versions.

Action:

Installed exact CUDA wheels:

```bash
uv pip install --python C:\Users\SED\Documents\new_my_ktmon\test5\.venv\Scripts\python.exe \
  --index-url https://download.pytorch.org/whl/cu121 \
  torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121
```

Restored compatibility pins:

```bash
uv pip install --python C:\Users\SED\Documents\new_my_ktmon\test5\.venv\Scripts\python.exe \
  numpy==1.26.4 pillow==10.4.0 markupsafe==2.1.5
```

### 7. llama-cpp-python CUDA wheel installed and DLL path fixed

Installed:

```bash
uv pip install --python C:\Users\SED\Documents\new_my_ktmon\test5\.venv\Scripts\python.exe \
  llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

Resolved runtime DLL loading by updating `gpu_config.py` to add PyTorch's `torch/lib` directory to the Windows DLL search path before `llama_cpp` imports.

## Final verification commands

```bash
uv pip check
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
python -c "from gpu_config import configure_gpu_for_project; configure_gpu_for_project(); import llama_cpp; print('llama_cpp OK')"
python -c "from kotaemon.base import BaseComponent; print('kotaemon OK')"
python -c "from ktem.main import App; print('ktem OK')"
python gpu_config.py --check
```

Verified output included:

- `torch 2.5.1+cu121 cuda 12.1 available True`
- `llama_cpp OK`
- `kotaemon OK`
- `ktem OK`
- `[OK] CUDA available: NVIDIA GeForce RTX 4090 Laptop GPU`
- `All installed packages are compatible`
