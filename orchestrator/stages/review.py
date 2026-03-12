"""Stage: review — run automated checks and produce verification + review artifacts."""

from __future__ import annotations

import subprocess
import sys

from orchestrator.artifacts import ArtifactStore
from orchestrator.llm.base import LLMProvider

SYSTEM_PROMPT = """\
You are a senior code reviewer and QA engineer.
Given a project plan and automated check results, produce:
1. A verification report (what passed, what failed, coverage notes)
2. A review report (code quality issues found, fixes applied, known limitations)

Be specific and actionable.  Output valid Markdown with clear headings.
"""

USER_PROMPT_TEMPLATE = """\
## Plan
{plan}

## Automated Check Results
```
{check_output}
```

Please produce the verification and review reports.
"""


def _run_checks() -> tuple[bool, str]:
    """Run ruff and pytest; return (passed, combined output)."""
    output_lines: list[str] = []
    all_passed = True

    for cmd in [
        [sys.executable, "-m", "ruff", "check", "."],
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
    ]:
        label = " ".join(cmd[1:])
        output_lines.append(f"=== {label} ===")
        try:
            result = subprocess.run(  # noqa: S603
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            output_lines.append(result.stdout)
            if result.returncode != 0:
                all_passed = False
                output_lines.append(result.stderr)
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            all_passed = False
            output_lines.append(f"ERROR running check: {exc}")

    return all_passed, "\n".join(output_lines)


def run(
    store: ArtifactStore,
    provider: LLMProvider,
    goal_issue: str = "",
    fixed_parts_path: str = "",
    **_kwargs: object,
) -> None:
    """Execute the review stage."""
    plan_content = store.read("plan")

    print("[review] Running automated checks (ruff + pytest) …")
    _passed, check_output = _run_checks()

    user_prompt = USER_PROMPT_TEMPLATE.format(
        plan=plan_content,
        check_output=check_output,
    )

    print("[review] Calling LLM to generate review artifacts …")
    content = provider.complete(SYSTEM_PROMPT, user_prompt)

    # Split combined LLM output into verification and review sections
    if "## Review" in content:
        parts = content.split("## Review", 1)
        verification_content = parts[0].strip()
        review_content = "## Review" + parts[1]
    else:
        verification_content = content
        review_content = content

    store.write("verification", verification_content)
    store.write("review", review_content)
