"""Gate enforcement: ensure stage prerequisites are satisfied."""

from __future__ import annotations

from orchestrator.artifacts import ArtifactStore

# Each stage requires these artifacts to already exist before running.
PREREQUISITES: dict[str, list[str]] = {
    "clarify": [],
    "solutions": ["goals", "requirements"],
    "design": ["goals", "requirements", "solution_options"],
    "plan": ["goals", "requirements", "solution_options", "design"],
    "review": ["goals", "requirements", "solution_options", "design", "plan"],
    "finalize": [
        "goals",
        "requirements",
        "solution_options",
        "design",
        "plan",
        "verification",
        "review",
    ],
}


class GateError(Exception):
    """Raised when stage prerequisites are not satisfied."""


def check_prerequisites(stage: str, store: ArtifactStore) -> None:
    """Raise GateError if required artifacts for *stage* are missing.

    Parameters
    ----------
    stage:
        One of the valid stage names.
    store:
        ArtifactStore to check.

    Raises
    ------
    GateError
        If any prerequisite artifact is absent.
    """
    required = PREREQUISITES.get(stage, [])
    missing = [artifact for artifact in required if not store.exists(artifact)]
    if missing:
        raise GateError(
            f"Stage '{stage}' requires the following artifacts which are missing: "
            + ", ".join(missing)
        )
