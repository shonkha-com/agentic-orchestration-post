# Agentic Orchestration Demo Setup

This folder contains two small `smolagents` examples for a public GitHub or LinkedIn post:

- `hello_smolagents_v4.py`: the agent uses one tool to find a GDP rank, then another tool to find the capital.
- `hello_smolagents_v5.py`: the agent uses a query-direction tool to get the ordered country list, then calls the capital tool.
- `session_logger.py`: writes each agent run to `logs/session_*.log`.

## Files Included

```text
agentic-orchestration-post/
  hello_smolagents_v4.py
  hello_smolagents_v5.py
  session_logger.py
  requirements.txt
  setup.md
  .gitignore
```

## Prerequisites

- Python 3.11 or 3.12 recommended.
- A model provider key:
  - Anthropic: set `ANTHROPIC_API_KEY`.
  - Hugging Face: set `HF_TOKEN` if you use the fallback `InferenceClientModel` path.

The scripts prefer Anthropic when `ANTHROPIC_API_KEY` is present. If it is not present, they use Hugging Face's inference client with `Qwen/Qwen2.5-Coder-32B-Instruct`.

## Install With uv

From this folder:

```powershell
pip install uv
uv venv .venv --python 3.11
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

If the folder is inside OneDrive and `uv` reports hardlink issues, run this before installing:

```powershell
$env:UV_LINK_MODE = "copy"
```

On macOS or Linux:

```bash
python3 -m pip install uv
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Set Your API Key

Anthropic on PowerShell:

```powershell
$env:ANTHROPIC_API_KEY = "your-anthropic-key"
```

Hugging Face on PowerShell:

```powershell
$env:HF_TOKEN = "your-huggingface-token"
```

macOS or Linux:

```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
# or
export HF_TOKEN="your-huggingface-token"
```

Do not commit real API keys to GitHub.

## Run The Examples

```powershell
python hello_smolagents_v4.py
python hello_smolagents_v5.py
```

Each run prints the final answer in the terminal and writes a timestamped trace under `logs/`.

## What To Look For

- In `v4`, the prompt asks for the country ranked number 3 by GDP, then asks for that country's capital.
- In `v5`, the prompt asks for the capital city of the country with the second largest economy.
- The interesting part is not the facts themselves. The useful teaching point is the agent orchestration pattern: the model has to select tools, call them in sequence, and use intermediate results.

## Troubleshooting

- `ModuleNotFoundError: smolagents`: activate the virtual environment and rerun `uv pip install -r requirements.txt`.
- Authentication or provider errors: confirm `ANTHROPIC_API_KEY` or `HF_TOKEN` is set in the same terminal where you run Python.
- PowerShell activation blocked: run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate the venv again.
- No `logs/` folder yet: it is created automatically after the first successful run.

## Public GitHub Checklist

- Keep `session_logger.py`; both examples import it.
- Keep `.gitignore`; generated logs can include prompts, model outputs, errors, and token counts.
- Do not commit `.env`, API keys, or personal session logs.
- Consider adding a `README.md`, `LICENSE`, and a short sample output before publishing the repo.
