"""Stage: solutions — propose multiple solution options with tradeoffs."""

from __future__ import annotations

from orchestrator.artifacts import ArtifactStore
from orchestrator.llm.base import LLMProvider

SYSTEM_PROMPT = """\
You are a senior software architect.
Given project requirements and acceptance criteria, propose 2–3 concrete solution options.
For each option provide:
- Overview / approach
- Architecture diagram (text-based)
- Key tradeoffs (speed, risk, cost, maintainability)
- What to reuse from fixed parts
- Estimated effort (rough T-shirt sizing)

Output valid Markdown with clear headings.
"""

USER_PROMPT_TEMPLATE = """\
## Requirements
{requirements}

## Fixed Parts / Integration Context
{fixed_parts}

Please propose solution options.
"""


def run(
    store: ArtifactStore,
    provider: LLMProvider,
    goal_issue: str = "",
    fixed_parts_path: str = "",
    **_kwargs: object,
) -> None:
    """Execute the solutions stage."""
    requirements = store.read("requirements")

    fixed_parts = ""
    if fixed_parts_path:
        from pathlib import Path

        fp = Path(fixed_parts_path)
        if fp.exists():
            fixed_parts = fp.read_text(encoding="utf-8")

    user_prompt = USER_PROMPT_TEMPLATE.format(
        requirements=requirements,
        fixed_parts=fixed_parts or "(none provided)",
    )

    print("[solutions] Calling LLM to generate solution options …")
    content = provider.complete(SYSTEM_PROMPT, user_prompt)
    store.write("solution_options", content)
