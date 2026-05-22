# Migration Notes: flat Python 3.11 project

## Summary

This migration converts the kotaemon fork from a uv workspace / monorepo package layout into a flat, editable `src/` project:

- `libs/kotaemon/kotaemon/` was copied to `src/kotaemon/`.
- `libs/ktem/ktem/` was copied to `src/ktem/`.
- `libs/` was intentionally kept for compatibility and comparison during migration.
- Root `pyproject.toml` is now the single package definition and dependency source for the app.
- `app.py` prepends `src/` to `sys.path`, so local source wins over stale `site-packages` copies.
- Python target was raised to `>=3.11` and `.python-version` was changed to `3.11`.
- GPU setup is separated from CPU/runtime dependencies; torch is not in `requirements.txt`.

## Step 0 reconnaissance evidence

### Packaging files read

- `pyproject.toml` (old root): `kotaemon-app`, Python `>=3.10`, depended on workspace packages `kotaemon[all]` and `ktem`.
- `libs/kotaemon/pyproject.toml`: core package dependencies plus optional `adv`, `dev`, `all` extras.
- `libs/ktem/pyproject.toml`: UI package dependencies.
- `Dockerfile`: Python `3.10-slim`, uv sync, extra installs for pdfservices-sdk, graphrag/future, CPU torch, `libs/kotaemon[adv]`, `unstructured[all-docs]`, LightRAG packages, and docling.
- `.env.example`, `app.py`, `flowsettings.py`, and `launch.sh` were read before edits.

### Requirements files found

- `libs/ktem/requirements.txt`:
  - `platformdirs`
  - `tzlocal`

### Direct imports in entry settings

- `app.py`: `from ktem.main import App`
- `flowsettings.py`: `from ktem.utils.lang import SUPPORTED_LANGUAGE_MAP`

`flowsettings.py` also contains string-based dotted references to `kotaemon.*` stores, LLMs, embeddings, rerankings, and to `ktem.*` reasoning/index classes.

## Dependency consolidation

The new root dependency list was built from:

1. `libs/kotaemon/pyproject.toml` base dependencies.
2. `libs/kotaemon/pyproject.toml` optional `adv` dependencies.
3. `libs/ktem/pyproject.toml` dependencies.
4. Old root `pyproject.toml` dependency intent, excluding internal `kotaemon` and `ktem` package dependencies.
5. `Dockerfile` pip/uv installs:
   - `pdfservices-sdk @ git+https://github.com/niallcm/pdfservices-python-sdk.git@bump-and-unfreeze-requirements`
   - `graphrag<=0.3.6`
   - `future`
   - `unstructured[all-docs]`
   - `aioboto3`
   - `nano-vectordb`
   - `ollama`
   - `xxhash`
   - `lightrag-hku<=1.3.0`
   - `docling<=2.5.2`
6. User-specified issue/documentation packages:
   - `graphrag`
   - `future`
   - `unstructured[all-docs]`
   - `lightrag-hku<=1.3.0`
   - `docling<=2.5.2`
   - `aioboto3`
   - `nano-vectordb`
   - `ollama`
   - `xxhash`

Deduplication choices:

- Internal `kotaemon`/`ktem` package dependencies were removed because both packages are now built from `src/`.
- `mcp` and `mcp[cli]` were deduplicated to `mcp[cli]>=1.0.0`.
- `python-decouple` was deduplicated to `python-decouple>=3.8,<4`.
- `unstructured` and `unstructured[all-docs]` were deduplicated to `unstructured[all-docs]>=0.16.0`.
- `torch`, `torchvision`, and `torchaudio` were excluded from `pyproject.toml` runtime dependencies and moved to `requirements-gpu.txt`.
- `sentence-transformers` and `llama-cpp-python` are GPU extras in `pyproject.toml` and handled by `requirements-gpu.txt`/README because they commonly pull or compile GPU-sensitive native dependencies.
- Existing upper bounds were preserved where the original project had explicit compatibility caps or where the user supplied a cap (`graphrag<=0.3.6`, `lightrag-hku<=1.3.0`, `docling<=2.5.2`).

## Files changed

- Added `src/kotaemon/` from `libs/kotaemon/kotaemon/`.
- Added `src/ktem/` from `libs/ktem/ktem/`.
- Added `tests/.gitkeep` so the flat layout has a root test directory.
- Rewrote `pyproject.toml` to use Hatchling and package `src/kotaemon` + `src/ktem`; enabled Hatch direct references for the existing Adobe `pdfservices-sdk` git dependency.
- Added `requirements.txt` for CPU/runtime dependencies without torch.
- Added `requirements-gpu.txt` for CUDA 12.1 torch and GPU-adjacent install notes.
- Added `requirements-dev.txt` for test/lint/dev dependencies.
- Added `gpu_config.py` with CUDA availability checks and TF32/Flash SDP enablement.
- Updated `app.py` to prepend `src/` to `sys.path` and call `configure_gpu_for_project()` before loading models.
- Updated `flowsettings.py` with safe `DEVICE` and `LLAMA_CPP_N_GPU_LAYERS` definitions.
- Updated `Dockerfile` to Python 3.11 and made the torch wheel index configurable, defaulting to CUDA 12.1 instead of CPU-only wheels.
- Updated `.python-version` to `3.11`.
- Added `Makefile` with install/install-gpu/run/dev targets.
- Replaced the README Installation section with Windows + CUDA instructions.

## Python 3.11 compatibility scan

Checked `src/` for removed/problematic patterns:

```bash
grep -RInE 'from distutils|import distutils|asyncio\.coroutine|import tomli|from tomli' src/
grep -RIn 'typing.Union\[' src/
```

No blocking occurrences were found.

## Validation run

Commands run after migration:

```bash
python3 - <<'PY'
import tomllib, pathlib
tomllib.loads(pathlib.Path('pyproject.toml').read_text())
print('pyproject.toml: TOML OK')
PY

PYTHONPATH=src python3 - <<'PY'
import importlib.util
for name in ['kotaemon', 'kotaemon.base', 'ktem', 'ktem.main']:
    spec = importlib.util.find_spec(name)
    print(name, 'FOUND' if spec else 'MISSING', getattr(spec, 'origin', None) if spec else '')
PY

python3 -m pip check

python3 -m venv /tmp/kotaemon-validate-venv
/tmp/kotaemon-validate-venv/bin/python -m pip install -U pip
/tmp/kotaemon-validate-venv/bin/python -m pip install -e . --no-deps --dry-run
```

Results:

- `pyproject.toml` parses as TOML.
- `kotaemon`, `kotaemon.base`, `ktem`, and `ktem.main` resolve from `src/` with `PYTHONPATH=src`.
- `python3 -m pip check` reported no broken requirements in the current environment.
- Editable package metadata generation succeeded in a temporary venv: `Would install kotaemon-0.1.0`.

The exact requested import commands could not complete in this bare environment because runtime dependencies are not installed here:

- `from kotaemon.base import BaseComponent` stops at missing `theflow`.
- `from ktem.main import App` stops at missing `gradio`.

After `uv pip install -e .` or `pip install -r requirements.txt && pip install -e .`, those imports should resolve against the new `src/` packages.


## Windows dependency fix

`unstructured[all-docs]` was relaxed to `>=0.16.0` because the old `<0.16` line pulled `pycrypto` through `layoutparser/pdfplumber`, which fails on Windows/Python 3.11.

- `duckduckgo-search` was pinned to `>=5.3.1,<6` on Windows/Python 3.11 to avoid `pyreqwest-impersonate` Rust/MSVC builds from 6.1.x.

- LangChain was pinned to the 0.2-compatible family because the project imports legacy modules such as `langchain.schema`, `langchain.agents.initialize_agent`, and `langchain.text_splitter` that are not present in LangChain 1.x.

- GPU install was verified with `torch==2.5.1+cu121`, `torchvision==0.20.1+cu121`, and `torchaudio==2.5.1+cu121`; `numpy==1.26.4`, `pillow==10.4.0`, and `markupsafe==2.1.5` were restored after torch reinstall to keep Gradio/Docling/LangChain constraints valid.

- `llama-cpp-python==0.3.4` was installed successfully from the CUDA 12.1 wheel index.

- `llama-cpp-python` is intentionally kept in `requirements-gpu.txt` instead of the `pyproject.toml` gpu extra because it needs the abetlen CUDA wheel index on Windows.
