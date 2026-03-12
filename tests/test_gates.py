"""Tests for gate enforcement."""

from __future__ import annotations

import pytest

from orchestrator.artifacts import ArtifactStore
from orchestrator.gates import GateError, check_prerequisites


@pytest.fixture()
def store(tmp_path):
    return ArtifactStore(base_dir=tmp_path)


def test_clarify_no_prerequisites(store):
    # clarify has no prerequisites — should always pass
    check_prerequisites("clarify", store)


def test_solutions_requires_goals_and_requirements(store):
    with pytest.raises(GateError) as exc_info:
        check_prerequisites("solutions", store)
    assert "goals" in str(exc_info.value)
    assert "requirements" in str(exc_info.value)


def test_solutions_passes_when_artifacts_present(store):
    store.write("goals", "# Goals")
    store.write("requirements", "# Requirements")
    check_prerequisites("solutions", store)  # should not raise


def test_design_requires_solution_options(store):
    store.write("goals", "# Goals")
    store.write("requirements", "# Requirements")
    with pytest.raises(GateError) as exc_info:
        check_prerequisites("design", store)
    assert "solution_options" in str(exc_info.value)


def test_plan_requires_design(store):
    store.write("goals", "# Goals")
    store.write("requirements", "# Requirements")
    store.write("solution_options", "# Options")
    with pytest.raises(GateError) as exc_info:
        check_prerequisites("plan", store)
    assert "design" in str(exc_info.value)


def test_review_requires_plan(store):
    store.write("goals", "# Goals")
    store.write("requirements", "# Requirements")
    store.write("solution_options", "# Options")
    store.write("design", "# Design")
    with pytest.raises(GateError) as exc_info:
        check_prerequisites("review", store)
    assert "plan" in str(exc_info.value)


def test_finalize_requires_all_artifacts(store):
    with pytest.raises(GateError):
        check_prerequisites("finalize", store)


def test_finalize_passes_when_all_present(store):
    artifacts = [
        "goals", "requirements", "solution_options",
        "design", "plan", "verification", "review",
    ]
    for artifact in artifacts:
        store.write(artifact, f"# {artifact}")
    check_prerequisites("finalize", store)  # should not raise


def test_gate_error_message_lists_all_missing(store):
    with pytest.raises(GateError) as exc_info:
        check_prerequisites("finalize", store)
    msg = str(exc_info.value)
    assert "goals" in msg
    assert "requirements" in msg
