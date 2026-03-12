"""Stage: plan — produce an ordered task breakdown + test plan."""

from __future__ import annotations

from orchestrator.artifacts import ArtifactStore
from orchestrator.llm.base import LLMProvider

SYSTEM_PROMPT = """\
You are a technical project manager.
Given requirements, solution options, and a design document, produce an execution plan:
- Ordered task list (each task mapped to one or more requirements / acceptance criteria)
- PR strategy (one PR vs. multiple)
- Test plan (unit / integration / e2e)
- Rollback plan
- Risk register (risk → likelihood → impact → mitigation)

Output valid Markdown with clear headings.
"""

USER_PROMPT_TEMPLATE = """\
## Requirements
{requirements}

## Solution Options
{solution_options}

## Design
{design}

Please produce the execution plan.
"""


def run(
    store: ArtifactStore,
    provider: LLMProvider,
    goal_issue: str = "",
    fixed_parts_path: str = "",
    **_kwargs: object,
) -> None:
    """Execute the plan stage."""
    requirements = store.read("requirements")
    solution_options = store.read("solution_options")
    design = store.read("design")

    user_prompt = USER_PROMPT_TEMPLATE.format(
        requirements=requirements,
        solution_options=solution_options,
        design=design,
    )

    print("[plan] Calling LLM to generate execution plan …")
    content = provider.complete(SYSTEM_PROMPT, user_prompt)
    store.write("plan", content)
