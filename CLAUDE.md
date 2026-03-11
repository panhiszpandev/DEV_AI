# DEV_AI - AI_devs 4: Builders

AI programming course in Python. 5 weeks, one lesson per working day.

## Project structure

- `lessons/` - lesson .md files (s01e01, s01e02, ...)
- `shared/` - shared modules
  - `ai_client.py` - OpenRouter API wrapper (functions `ask` and `ask_json`)
  - `hub_client.py` - hub.ag3nts.org client (functions `verify` and `get_data`)
- `prompts/` - shared system prompts in .md files
- `s01e01/`, `s01e02/`, ... - task solution folders
  - `main.py` - script to run
  - `prompts/` - task-specific prompts
  - `README.md` - task description with flow diagram (Mermaid)

## Creating a new lesson folder

When creating a new lesson folder (e.g. `s01e03/`), always include a `README.md` following the same structure as `s01e01/README.md`:
- short description of what the program does
- numbered list of steps
- Mermaid flow diagram
- run instructions

## API keys

Stored in `.env` (not in git):
- `OPENAI_API_KEY` - OpenRouter key (used for all models via OpenRouter)
- `HUB_API_KEY` - key from https://hub.ag3nts.org/

## Running tasks

```bash
cd s01e01
python main.py
```

## Submitting answers to the Hub

Use `hub_client.verify(task, answer)`. Response contains a flag in format `{FLG:...}`.

## Local config

See `.claude-private.md` for additional instructions (local only, not in git).
