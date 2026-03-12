"""Stage: clarify — analyze goals and produce requirements + acceptance criteria."""

from __future__ import annotations

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
) -> None:
    """Execute the clarify stage."""
    # Ensure goals artifact exists (seed from template if missing)
    if not store.exists("goals"):
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
