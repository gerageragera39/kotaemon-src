# Новый запуск проекта и виртуальное окружение

Проект переведён на плоскую структуру `src/`, поэтому локальный код загружается из текущего git checkout, а не из старых копий `libs/*` в `site-packages`.

## Требования

- Python 3.11
- Git
- `uv` для быстрой установки зависимостей
- Для GPU: NVIDIA CUDA 12.1+ и совместимый драйвер

## 1. Установка `uv`

```bash
pip install uv
```

Проверь установку:

```bash
uv --version
```

## 2. Создание виртуального окружения

### Windows PowerShell / CMD

```bash
uv venv .venv --python 3.11
.venv\Scripts\activate
```

### Linux / macOS

```bash
uv venv .venv --python 3.11
source .venv/bin/activate
```

После активации проверь Python:

```bash
python --version
```

Ожидается Python `3.11.x`.

## 3. Установка зависимостей CPU

CPU-вариант не устанавливает `torch` отдельно:

```bash
uv pip install -e .
```

Альтернатива через requirements:

```bash
uv pip install -r requirements.txt
uv pip install -e . --no-deps
```

## 4. Установка зависимостей GPU на Windows / CUDA 12.1

Сначала установи CUDA-версию PyTorch:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Затем установи проект:

```bash
uv pip install -e .
```

Или одной командой через файл GPU-зависимостей:

```bash
uv pip install -r requirements-gpu.txt
uv pip install -e .
```

### llama-cpp-python с CUDA

На Windows CUDA-сборку `llama-cpp-python` лучше ставить отдельно:

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

## 5. Проверка GPU

```bash
python gpu_config.py --check
```

Если CUDA доступна, будет показано имя GPU, версия CUDA и объём VRAM.

Если CUDA недоступна, приложение всё равно может работать в CPU-режиме.

## 6. Запуск приложения

```bash
python app.py
```

По умолчанию `app.py` добавляет `src/` в `sys.path`, поэтому используются локальные пакеты:

- `src/kotaemon`
- `src/ktem`

## 7. Запуск через Makefile

### CPU

```bash
make install
make run
```

### GPU

```bash
make install-gpu
make run
```

> На Windows команды `make` доступны, если установлен GNU Make. Если Make недоступен, используй команды из разделов выше напрямую.

## 8. Проверка импортов

После установки зависимостей проверь:

```bash
python -c "from kotaemon.base import BaseComponent; print('kotaemon OK')"
python -c "from ktem.main import App; print('ktem OK')"
```

## 9. Частые проблемы

### `python` не найден

Проверь, что окружение активировано:

```bash
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/macOS
```

### Неверная версия Python

Пересоздай окружение:

```bash
rm -rf .venv                # Linux/macOS
# или удали папку .venv вручную на Windows
uv venv .venv --python 3.11
```

### CUDA не видна

Проверь:

```bash
python gpu_config.py --check
python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
```

Если `False`, переустанови PyTorch CUDA wheel:

```bash
pip uninstall -y torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Ошибки сборки на Windows

Установи Microsoft C++ Build Tools:

<https://visualstudio.microsoft.com/visual-cpp-build-tools/>

Это часто требуется для `chromadb`, `grpcio`, `llama-cpp-python` и других native-зависимостей.

## 10. Обновление после смены git-коммита

Так как проект ставится editable-режимом (`uv pip install -e .`), код берётся из текущей рабочей директории.

После `git pull` обычно достаточно перезапустить приложение:

```bash
python app.py
```

Если изменились зависимости:

```bash
uv pip install -e .
```


## 11. Optional-интеграции с конфликтующими зависимостями

Базовая установка исключает две optional-интеграции, потому что их текущие metadata конфликтуют с Gradio 4.x:

- Adobe PDF Services SDK: `requirements-adobe.txt` (`urllib3<1.27` против `urllib3>=2` у Gradio).
- Microsoft GraphRAG: `requirements-graphrag.txt` (`aiofiles>=24.1` против `aiofiles<24` у Gradio 4.x).

Поэтому `USE_MS_GRAPHRAG` по умолчанию выключен. Для экспериментов с этими интеграциями лучше использовать отдельное окружение или ждать совместимых версий пакетов.


## 12. Windows dependency note

`unstructured[all-docs]` is kept at `>=0.16.0` to avoid the obsolete `pycrypto` build path on Windows/Python 3.11.


## 13. Проверенные GPU-версии в этом окружении

В `.venv` проверены CUDA wheels:

- `torch==2.5.1+cu121`
- `torchvision==0.20.1+cu121`
- `torchaudio==2.5.1+cu121`

`python gpu_config.py --check` должен показывать CUDA 12.1 и имя видеокарты.

- `llama-cpp-python==0.3.4` установлен из CUDA wheel index `https://abetlen.github.io/llama-cpp-python/whl/cu121`.

- `llama-cpp-python` is intentionally kept in `requirements-gpu.txt` instead of the `pyproject.toml` gpu extra because it needs the abetlen CUDA wheel index on Windows.
