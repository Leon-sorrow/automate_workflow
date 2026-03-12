"""Stage: finalize — produce the human checklist for final sign-off."""

from __future__ import annotations

from orchestrator.artifacts import ArtifactStore
from orchestrator.llm.base import LLMProvider

SYSTEM_PROMPT = """\
You are a release manager.
Given all previous project artifacts, produce a concise human checklist for final sign-off.
The checklist should cover:
- Functional checks (things the human should verify manually)
- Non-functional checks (performance, security, scalability)
- Deployment / release steps
- Rollback instructions
- Documentation / communication tasks

Output valid Markdown with clear headings and checkboxes (- [ ] …).
"""

USER_PROMPT_TEMPLATE = """\
## Goals
{goals}

## Requirements
{requirements}

## Design
{design}

## Plan
{plan}

## Verification
{verification}

## Review
{review}

Please produce the human sign-off checklist.
"""


def run(
    store: ArtifactStore,
    provider: LLMProvider,
    goal_issue: str = "",
    fixed_parts_path: str = "",
) -> None:
    """Execute the finalize stage."""
    user_prompt = USER_PROMPT_TEMPLATE.format(
        goals=store.read("goals"),
        requirements=store.read("requirements"),
        design=store.read("design"),
        plan=store.read("plan"),
        verification=store.read("verification"),
        review=store.read("review"),
    )

    print("[finalize] Calling LLM to generate human checklist …")
    content = provider.complete(SYSTEM_PROMPT, user_prompt)
    store.write("human_checklist", content)
