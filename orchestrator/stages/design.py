"""Stage: design — produce detailed design spec from chosen solution option."""

from __future__ import annotations

from orchestrator.artifacts import ArtifactStore
from orchestrator.llm.base import LLMProvider

SYSTEM_PROMPT = """\
You are a senior software architect producing a detailed design document.
Given requirements and solution options, produce a design document covering:
- Module boundaries and responsibilities
- API / function signatures (key interfaces)
- Data model
- Error handling contract
- Configuration and secrets
- Observability and logging plan
- Migration plan (if applicable)

The design should have enough detail to implement without inventing new requirements.
Output valid Markdown with clear headings.
"""

USER_PROMPT_TEMPLATE = """\
## Requirements
{requirements}

## Solution Options
{solution_options}

## Fixed Parts / Integration Context
{fixed_parts}

Please produce the design document.
"""


def run(
    store: ArtifactStore,
    provider: LLMProvider,
    goal_issue: str = "",
    fixed_parts_path: str = "",
    **_kwargs: object,
) -> None:
    """Execute the design stage."""
    requirements = store.read("requirements")
    solution_options = store.read("solution_options")

    fixed_parts = ""
    if fixed_parts_path:
        from pathlib import Path

        fp = Path(fixed_parts_path)
        if fp.exists():
            fixed_parts = fp.read_text(encoding="utf-8")

    user_prompt = USER_PROMPT_TEMPLATE.format(
        requirements=requirements,
        solution_options=solution_options,
        fixed_parts=fixed_parts or "(none provided)",
    )

    print("[design] Calling LLM to generate design document …")
    content = provider.complete(SYSTEM_PROMPT, user_prompt)
    store.write("design", content)
