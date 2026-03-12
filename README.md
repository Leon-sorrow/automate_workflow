# Auto Project Workflow

A GitHub Actions–based **auto project workflow** scaffold that guides a project
through a staged lifecycle with human gates and LLM-assisted artifact generation.

This scaffold supports:
- **New projects** (start from goals → generate requirements/design/plan)
- **Improving an existing project** (provide an existing project URL and constraints, then generate structured artifacts)

## Quick start

### What you should provide

**Required**
- `project/01_goals.md` — your goals for the work.

  You can provide this in three ways (in order of precedence):
  1. **Via `--goals` CLI flag** (or the **goals** input in the Actions UI) — paste your goal text directly.
  2. **Edit the file first** — copy `project/templates/01_goals.md` to `project/01_goals.md` and fill it in.
  3. **Interactive prompt** — when running locally in a terminal without a pre-existing goals file, the CLI prompts you to enter goals section-by-section.

**Optional (recommended for improving an existing project)**
- **existing_project_url** — URL of the existing project/repo you want to improve (entered in the Actions UI).
  - Example: `https://github.com/org/repo`

**Optional**
- **goals** — project goals text; pasted directly into the Actions UI or passed via `--goals` on the CLI (fills `project/01_goals.md` if not already set)
- **goal_issue** — issue number or URL to seed goals context
- **fixed_parts_path** — path to an existing component description / architecture notes
- **model** — GitHub Models model name (default: `"default"` → `gpt-4o-mini`)
- **allow_stub** — when `true` (default), writes stub artifacts if LLM is unavailable

### Run from the GitHub Actions UI (recommended)

1. Go to **Actions → Project Orchestrator → Run workflow**.
2. Fill in the inputs:
   - **stage** – which stage to run (start with `clarify`)
   - **goals** *(optional)* – paste your project goals text directly; the workflow writes it to `project/01_goals.md` before running
   - **existing_project_url** *(optional)* – existing project/repo URL you want to improve
   - **goal_issue** *(optional)*
   - **fixed_parts_path** *(optional)*
   - **model** *(optional)*
   - **allow_stub** *(optional)*
3. Run the workflow.
4. The workflow commits any new artifacts back to the branch automatically under `project/`.

### Typical run order

```
clarify → solutions → (human picks option) → design → plan → review → finalize
```

Between `solutions` and `design` you must manually edit
`project/03_solution_options.md` to mark your chosen option before running `design`.

## Lifecycle stages

| # | Stage | Human action required | Artifacts produced |
|---|-------|-----------------------|--------------------|
| 1 | `clarify` | Propose goals (edit `project/01_goals.md` first) | `02_requirements.md` |
| 2 | `solutions` | Review & pick a solution option | `03_solution_options.md` |
| 3 | `design` | Review & approve design | `04_design.md` |
| 4 | `plan` | Review & approve plan | `05_plan.md` |
| 5 | `review` | Review check results | `07_verification.md`, `08_review.md` |
| 6 | `finalize` | Final sign-off | `09_human_checklist.md` |

Each stage **enforces prerequisites**: if earlier artifacts are missing the
workflow exits with a clear error message so nothing proceeds until the
previous step is complete.

## Configuring GitHub Models access

1. Ensure your repository has a **`GITHUB_TOKEN`** with `models:read` permission
   (the default Actions token already has this for public repositories or if
   GitHub Models is enabled for your org/account).
2. Set the `model` input to the model slug you want to use, e.g. `gpt-4o`,
   `gpt-4o-mini`, `meta-llama-3.1-405b-instruct`, etc. Leave it as `"default"`
   to use `gpt-4o-mini`.
3. If the LLM call fails (token missing, quota exceeded, …) and `allow_stub=true`,
   stub files are written with a `[STUB]` marker so you can fill them in manually.

### Using a different LLM provider

`orchestrator/llm/base.py` defines the `LLMProvider` ABC. Create a new class
that implements `complete(system_prompt, user_prompt) -> str` and pass an
instance of it where `GitHubModelsProvider` is currently used in `cli.py`.

## Running locally

```bash
pip install -e ".[dev]"

# Option 1: pass goals directly via --goals flag
python -m orchestrator --stage clarify --goals "My project goal: build a REST API"

# Option 2: pre-create the goals file
cp project/templates/01_goals.md project/01_goals.md
# edit project/01_goals.md …
python -m orchestrator --stage clarify

# Option 3: run interactively — the CLI prompts for goals if the file is missing
python -m orchestrator --stage clarify

python -m orchestrator --stage solutions
# … etc.
```

## CI

The `ci.yml` workflow runs **ruff** (linting) and **pytest** on every push and
pull request.

```bash
ruff check .
pytest tests/ -v
```

## Project layout

```
.github/
  workflows/
    project-orchestrator.yml   # main orchestration workflow
    ci.yml                     # lint + test
orchestrator/
  cli.py                       # argument parsing + entry point
  artifacts.py                 # read/write project/*.md
  gates.py                     # prerequisite enforcement
  stages/
    clarify.py
    solutions.py
    design.py
    plan.py
    review.py
    finalize.py
  llm/
    base.py                    # LLMProvider ABC
    github_models.py           # GitHub Models (Azure) provider
project/
  templates/                   # blank templates for each artifact
  01_goals.md                  # (you write this first)
  02_requirements.md           # generated by clarify
  …
tests/                         # pytest unit tests
pyproject.toml                 # ruff + pytest config
```