# DEV_AI - AI_devs 4: Builders

AI programming course in Python. 5 weeks, one lesson per working day.

## Project structure

- `lessons/` - lesson .md files (s01e01, s01e02, ...)
- `shared/` - shared modules
  - `ai_client.py` - OpenRouter API wrapper (functions `ask` and `ask_json`)
  - `hub_client.py` - hub.ag3nts.org client (functions `verify` and `get_data`)
- `prompts/` - shared system prompts in .md files
- `s01e01/`, `s01e02/`, ... - task solution folders
  - `main.py` - script to run (no `load_dotenv()` — handled by shared modules)
  - `prompts/` - task-specific prompts in .md files
    - `system.md` - system prompt for the agent
    - `task.md` - user/task prompt (if using agent loop)
  - `tools/` - tool classes, one per file, each with `schema()` and `run()` methods
  - `data/` - task input data (parameters, shipment details, etc.) — not prompts
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

## Language

All code, comments, prompts, and documentation must be written in English. Exception: data values sent to external servers (e.g. city names, shipment contents, API payloads) should remain as-is.

## Git workflow

- Each lesson gets its own branch (e.g. `s02e01`)
- Changes to `sXXeYY/` and `shared/` go through pull requests — no direct pushes to `main`
- Documentation and config files (`CLAUDE.md`, `requirements.txt`, `.gitignore`, etc.) may be pushed directly to `main`
- PRs are merged using **squash merge**

### Commit style (on feature branch)

Use short imperative sentences without a type prefix:

```
Add FetchItemsTool, ResetBudgetTool, ClassifyAllTool
Add main.py with agent engineer loop
Add system and task prompts
Add README with flow diagram
```

### Squash commit (on main after merge)

Title: `sXXeYY: Short description of what the lesson does (#N)`
Body: list of individual branch commits:

```
s02e01: Cargo classifier agent with iterative prompt engineering (#5)

- Add FetchItemsTool, ResetBudgetTool, ClassifyAllTool
- Add main.py with agent engineer loop
- Add system and task prompts
- Add README with flow diagram
```

## Local config

See `.claude-private.md` for additional instructions (local only, not in git).
