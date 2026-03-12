"""Stage: clarify — analyze goals and produce requirements + acceptance criteria."""

from __future__ import annotations

import sys

from orchestrator.artifacts import ArtifactStore
from orchestrator.llm.base import LLMProvider

SYSTEM_PROMPT = """\
You are an expert requirements analyst.
Your job is to read a project goal statement and produce:
1. Clarifying questions that would help refine the requirements.
2. Functional and non-functional requirements.
3. Testable acceptance criteria for each requirement.
4. An explicit out-of-scope list.

Output valid Markdown with clear headings.
"""

USER_PROMPT_TEMPLATE = """\
## Project Goals
{goals}

## Fixed Parts / Integration Context
{fixed_parts}

Please produce the requirements document as described.
"""

STUB_REQUIREMENTS = """\
# Requirements

> **[STUB]** Fill in requirements after running the clarify stage with a valid LLM.

## Clarifying Questions
- [ ] What is the primary user or audience?
- [ ] What are the performance requirements?
- [ ] What integrations are required?

## Functional Requirements
- FR-01: (describe)

## Non-Functional Requirements
- NFR-01: (describe)

## Acceptance Criteria
- AC-01: Given … when … then …

## Out of Scope
- (list items)
"""


def run(
    store: ArtifactStore,
    provider: LLMProvider,
    goal_issue: str = "",
    fixed_parts_path: str = "",
    goals: str = "",
    **_kwargs: object,
) -> None:
    """Execute the clarify stage."""
    # Ensure goals artifact exists (seed from provided text, interactive input, template, or stub)
    if not store.exists("goals"):
        if goals:
            store.write("goals", goals)
        elif sys.stdin.isatty():
            store.write("goals", _prompt_goals_interactively(goal_issue))
        else:
            template = store.read_template("01_goals")
            store.write("goals", template or _default_goals_stub(goal_issue))

    goals_content = store.read("goals")

    fixed_parts = ""
    if fixed_parts_path:
        from pathlib import Path

        fp = Path(fixed_parts_path)
        if fp.exists():
            fixed_parts = fp.read_text(encoding="utf-8")
        else:
            print(f"[clarify] Warning: fixed_parts_path '{fixed_parts_path}' not found.")

    user_prompt = USER_PROMPT_TEMPLATE.format(
        goals=goals_content,
        fixed_parts=fixed_parts or "(none provided)",
    )

    print("[clarify] Calling LLM to generate requirements …")
    content = provider.complete(SYSTEM_PROMPT, user_prompt)
    store.write("requirements", content)


def _default_goals_stub(goal_issue: str) -> str:
    issue_ref = f"\n\nRef: {goal_issue}" if goal_issue else ""
    return f"""\
# Project Goals

> **[STUB]** Replace this file with your actual project goals.

## Goals
- Goal 1: (describe)
- Goal 2: (describe)

## Constraints
- (list constraints)

## Definition of Done
- (describe){issue_ref}
"""


def _collect_lines(prompt: str) -> list[str]:
    """Collect non-empty lines from stdin until an empty line is entered."""
    print(f"\n{prompt}")
    print("  (enter each item on its own line; empty line to finish)")
    lines: list[str] = []
    while True:
        try:
            line = input("  > ")
        except EOFError:
            break
        stripped = line.strip()
        if not stripped:
            break
        lines.append(stripped)
    return lines


def _prompt_goals_interactively(goal_issue: str) -> str:
    """Interactively collect project goals from the user via stdin."""
    print("\n[clarify] No project goals file found.")
    print("[clarify] Please enter your project goals interactively.")
    print("[clarify] Press Enter on an empty line to move to the next section.\n")

    goals_lines = _collect_lines("Goals — what should this project achieve?")
    constraints_lines = _collect_lines("Constraints (tech stack, time, budget, etc.)")
    dod_lines = _collect_lines("Definition of Done — what does 'finished' look like?")

    def fmt(lines: list[str]) -> str:
        return "\n".join(f"- {line}" for line in lines) if lines else "- (not provided)"

    issue_ref = f"\n\n## References\n- {goal_issue}" if goal_issue else ""
    return (
        "# Project Goals\n\n"
        "## Goals\n"
        f"{fmt(goals_lines)}\n\n"
        "## Constraints\n"
        f"{fmt(constraints_lines)}\n\n"
        "## Definition of Done\n"
        f"{fmt(dod_lines)}"
        f"{issue_ref}\n"
    )
