"""CLI argument parsing for the orchestrator."""

import argparse
import sys

from orchestrator import stages
from orchestrator.artifacts import ArtifactStore
from orchestrator.gates import GateError, check_prerequisites
from orchestrator.llm.github_models import GitHubModelsProvider

STAGES = ["clarify", "solutions", "design", "plan", "review", "finalize"]

STAGE_MODULES = {
    "clarify": stages.clarify,
    "solutions": stages.solutions,
    "design": stages.design,
    "plan": stages.plan,
    "review": stages.review,
    "finalize": stages.finalize,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="orchestrator",
        description="Auto project workflow orchestrator",
    )
    parser.add_argument(
        "--stage",
        required=True,
        choices=STAGES,
        help="Workflow stage to execute",
    )
    parser.add_argument(
        "--model",
        default="default",
        help="GitHub Models model name (default: 'default')",
    )
    parser.add_argument(
        "--allow-stub",
        action="store_true",
        default=True,
        help="Write stub artifacts if LLM is unavailable",
    )
    parser.add_argument(
        "--no-allow-stub",
        dest="allow_stub",
        action="store_false",
        help="Fail instead of writing stub artifacts",
    )
    parser.add_argument(
        "--existing-project-url",
        default="",
        help="Existing project URL to improve (optional)",
    )
    parser.add_argument(
        "--goals",
        default="",
        help="Project goals text (written to project/01_goals.md if not already set)",
    )
    parser.add_argument(
        "--goal-issue",
        default="",
        help="GitHub issue number or URL to seed goals",
    )
    parser.add_argument(
        "--fixed-parts-path",
        default="",
        help="Path to fixed parts documentation file",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    store = ArtifactStore()
    provider = GitHubModelsProvider(model=args.model, allow_stub=args.allow_stub)

    try:
        check_prerequisites(args.stage, store)
    except GateError as exc:
        print(f"[gate] Prerequisites not met for stage '{args.stage}': {exc}", file=sys.stderr)
        sys.exit(1)

    module = STAGE_MODULES[args.stage]
    module.run(
        store=store,
        provider=provider,
        goal_issue=args.goal_issue,
        goals=args.goals,
        fixed_parts_path=args.fixed_parts_path,
        existing_project_url=args.existing_project_url,
    )
    print(f"[orchestrator] Stage '{args.stage}' completed successfully.")
