<div align="center">

# kotaemon

An open-source clean & customizable RAG UI for chatting with your documents. Built with both end users and
developers in mind.

![Preview](https://raw.githubusercontent.com/Cinnamon/kotaemon/main/docs/images/preview-graph.png)

<a href="https://trendshift.io/repositories/11607" target="_blank"><img src="https://trendshift.io/api/badge/repositories/11607" alt="Cinnamon%2Fkotaemon | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

[Live Demo #1](https://huggingface.co/spaces/cin-model/kotaemon) |
[Live Demo #2](https://huggingface.co/spaces/cin-model/kotaemon-demo) |
[Online Install](https://cinnamon.github.io/kotaemon/online_install/) |
[Colab Notebook (Local RAG)](https://colab.research.google.com/drive/1eTfieec_UOowNizTJA1NjawBJH9y_1nn)

[User Guide](https://cinnamon.github.io/kotaemon/) |
[Developer Guide](https://cinnamon.github.io/kotaemon/development/) |
[Feedback](https://github.com/Cinnamon/kotaemon/issues) |
[Contact](mailto:kotaemon.support@cinnamon.is)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-31013/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<a href="https://github.com/Cinnamon/kotaemon/pkgs/container/kotaemon" target="_blank">
<img src="https://img.shields.io/badge/docker_pull-kotaemon:latest-brightgreen" alt="docker pull ghcr.io/cinnamon/kotaemon:latest"></a>
![download](https://img.shields.io/github/downloads/Cinnamon/kotaemon/total.svg?label=downloads&color=blue)
<a href='https://huggingface.co/spaces/cin-model/kotaemon-demo'><img src='https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue'></a>
<a href="https://hellogithub.com/en/repository/d3141471a0244d5798bc654982b263eb" target="_blank"><img src="https://abroad.hellogithub.com/v1/widgets/recommend.svg?rid=d3141471a0244d5798bc654982b263eb&claim_uid=RLiD9UZ1rEHNaMf&theme=small" alt="Featured｜HelloGitHub" /></a>

</div>

<!-- start-intro -->

## Introduction

This project serves as a functional RAG UI for both end users who want to do QA on their
documents and developers who want to build their own RAG pipeline.
<br>

```yml
+----------------------------------------------------------------------------+
| End users: Those who use apps built with `kotaemon`.                       |
| (You use an app like the one in the demo above)                            |
|     +----------------------------------------------------------------+     |
|     | Developers: Those who built with `kotaemon`.                   |     |
|     | (You have `import kotaemon` somewhere in your project)         |     |
|     |     +----------------------------------------------------+     |     |
|     |     | Contributors: Those who make `kotaemon` better.    |     |     |
|     |     | (You make PR to this repo)                         |     |     |
|     |     +----------------------------------------------------+     |     |
|     +----------------------------------------------------------------+     |
+----------------------------------------------------------------------------+
```

### For end users

- **Clean & Minimalistic UI**: A user-friendly interface for RAG-based QA.
- **Support for Various LLMs**: Compatible with LLM API providers (OpenAI, AzureOpenAI, Cohere, etc.) and local LLMs (via `ollama` and `llama-cpp-python`).
- **Easy Installation**: Simple scripts to get you started quickly.

### For developers

- **Framework for RAG Pipelines**: Tools to build your own RAG-based document QA pipeline.
- **Customizable UI**: See your RAG pipeline in action with the provided UI, built with <a href='https://github.com/gradio-app/gradio'>Gradio <img src='https://img.shields.io/github/stars/gradio-app/gradio'></a>.
- **Gradio Theme**: If you use Gradio for development, check out our theme here: [kotaemon-gradio-theme](https://github.com/lone17/kotaemon-gradio-theme).

## Key Features

- **Host your own document QA (RAG) web-UI**: Support multi-user login, organize your files in private/public collections, collaborate and share your favorite chat with others.

- **Organize your LLM & Embedding models**: Support both local LLMs & popular API providers (OpenAI, Azure, Ollama, Groq).

- **Hybrid RAG pipeline**: Sane default RAG pipeline with hybrid (full-text & vector) retriever and re-ranking to ensure best retrieval quality.

- **Multi-modal QA support**: Perform Question Answering on multiple documents with figures and tables support. Support multi-modal document parsing (selectable options on UI).

- **Advanced citations with document preview**: By default the system will provide detailed citations to ensure the correctness of LLM answers. View your citations (incl. relevant score) directly in the _in-browser PDF viewer_ with highlights. Warning when retrieval pipeline return low relevant articles.

- **Support complex reasoning methods**: Use question decomposition to answer your complex/multi-hop question. Support agent-based reasoning with `ReAct`, `ReWOO` and other agents.

- **Configurable settings UI**: You can adjust most important aspects of retrieval & generation process on the UI (incl. prompts).

- **Extensible**: Being built on Gradio, you are free to customize or add any UI elements as you like. Also, we aim to support multiple strategies for document indexing & retrieval. `GraphRAG` indexing pipeline is provided as an example.

![Preview](https://raw.githubusercontent.com/Cinnamon/kotaemon/main/docs/images/preview.png)

## Installation

## Установка на Windows с GPU (CUDA)

### Требования

- Python 3.11 (<https://python.org/downloads/>)
- CUDA 12.1+ (<https://developer.nvidia.com/cuda-downloads>)
- cuDNN 8.9+ (<https://developer.nvidia.com/cudnn>)
- Git

### Шаги

```bash
# 1. Клонировать
git clone https://github.com/YOUR_FORK/kotaemon
cd kotaemon

# 2. Установить uv (быстрее pip)
pip install uv

# 3. Создать окружение на Python 3.11
uv venv .venv --python 3.11

# 4. Активировать (Windows)
.venv\Scripts\activate

# 5a. GPU (NVIDIA) — установить torch с CUDA сначала
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 5b. Установить остальные зависимости из плоского проекта
uv pip install -e .

# 6. Проверить GPU
python gpu_config.py --check

# 7. Запустить
python app.py
```

### CPU / без CUDA

```bash
pip install uv
uv venv .venv --python 3.11
.venv\Scripts\activate
uv pip install -e .
python app.py
```

### Альтернативно через requirements

```bash
# CPU/runtime без torch
pip install -r requirements.txt

# GPU: сначала CUDA torch, затем runtime/project
pip install -r requirements-gpu.txt
pip install -e .
```

### Частые ошибки Windows

**Microsoft Visual C++ required** (для `chromadb`, `grpcio`):
→ Установи Build Tools: <https://visualstudio.microsoft.com/visual-cpp-build-tools/>

**`grpcio` не ставится**:
→ Попробуй предварительный wheel:

```bash
pip install grpcio --pre --extra-index-url https://packages.grpc.io/
```

**`llama-cpp-python` с GPU**:
→ На Windows с CUDA устанавливай отдельным wheel-индексом, а не обычным CPU wheel:

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

### Что изменилось в структуре

Код внутренних пакетов теперь живёт в `src/kotaemon` и `src/ktem`, поэтому локальный запуск и `pip install -e .` используют текущий git checkout, а не замороженную копию из `site-packages`. Старый каталог `libs/` оставлен для совместимости и сравнения во время миграции.

## Citation

Please cite this project as

```BibTeX
@misc{kotaemon2024,
    title = {Kotaemon - An open-source RAG-based tool for chatting with any content.},
    author = {The Kotaemon Team},
    year = {2024},
    howpublished = {\url{https://github.com/Cinnamon/kotaemon}},
}
```

## Star History

<a href="https://star-history.com/#Cinnamon/kotaemon&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Cinnamon/kotaemon&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Cinnamon/kotaemon&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Cinnamon/kotaemon&type=Date" />
 </picture>
</a>

## Contribution

Since our project is actively being developed, we greatly value your feedback and contributions. Please see our [Contributing Guide](https://github.com/Cinnamon/kotaemon/blob/main/CONTRIBUTING.md) to get started. Thank you to all our contributors!

<a href="https://github.com/Cinnamon/kotaemon/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Cinnamon/kotaemon" />
</a>
