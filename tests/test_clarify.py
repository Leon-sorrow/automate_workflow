"""Tests for the clarify stage goal collection behaviour."""

from __future__ import annotations

import io

import pytest

from orchestrator.artifacts import ArtifactStore
from orchestrator.llm.github_models import GitHubModelsProvider
from orchestrator.stages.clarify import (
    _collect_lines,
    _default_goals_stub,
    _prompt_goals_interactively,
    run,
)

# ---------------------------------------------------------------------------
# _default_goals_stub
# ---------------------------------------------------------------------------


def test_default_goals_stub_no_issue():
    result = _default_goals_stub("")
    assert "# Project Goals" in result
    assert "[STUB]" in result
    assert "Ref:" not in result


def test_default_goals_stub_with_issue():
    result = _default_goals_stub("https://github.com/org/repo/issues/42")
    assert "Ref: https://github.com/org/repo/issues/42" in result


# ---------------------------------------------------------------------------
# _collect_lines
# ---------------------------------------------------------------------------


def test_collect_lines_stops_on_empty_line(monkeypatch):
    inputs = iter(["First item", "Second item", "", "ignored"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))
    lines = _collect_lines("Test prompt")
    assert lines == ["First item", "Second item"]


def test_collect_lines_stops_on_eof(monkeypatch):
    def raise_eof(_prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)
    lines = _collect_lines("Test prompt")
    assert lines == []


# ---------------------------------------------------------------------------
# _prompt_goals_interactively
# ---------------------------------------------------------------------------


def test_prompt_goals_interactively_builds_markdown(monkeypatch):
    # Simulate user input: goals, empty, constraints, empty, dod, empty
    responses = iter(
        [
            "Build a chat app",
            "",  # end goals
            "Python only",
            "",  # end constraints
            "Users can send messages",
            "",  # end dod
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(responses))
    result = _prompt_goals_interactively("")
    assert "# Project Goals" in result
    assert "- Build a chat app" in result
    assert "- Python only" in result
    assert "- Users can send messages" in result


def test_prompt_goals_interactively_includes_issue_ref(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt="": "")
    result = _prompt_goals_interactively("https://github.com/org/repo/issues/7")
    assert "https://github.com/org/repo/issues/7" in result


# ---------------------------------------------------------------------------
# run() — goals parameter
# ---------------------------------------------------------------------------


@pytest.fixture()
def store(tmp_path):
    return ArtifactStore(base_dir=tmp_path)


@pytest.fixture()
def stub_provider(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    return GitHubModelsProvider(allow_stub=True)


def test_run_uses_goals_kwarg(store, stub_provider):
    """When goals kwarg is provided it is written to the goals artifact."""
    goals_text = "# Custom Goals\n- Ship fast\n"
    run(store=store, provider=stub_provider, goals=goals_text)
    assert "Ship fast" in store.read("goals")


def test_run_goals_kwarg_not_overwritten_when_file_exists(store, stub_provider):
    """Existing goals file is not replaced by goals kwarg."""
    store.write("goals", "# Existing\n")
    run(store=store, provider=stub_provider, goals="New goals")
    assert "Existing" in store.read("goals")


def test_run_falls_back_to_stub_in_non_tty(store, stub_provider, monkeypatch):
    """In non-interactive mode without --goals, the stub/template is used."""
    monkeypatch.setattr("sys.stdin", io.StringIO(""))  # non-TTY stdin
    run(store=store, provider=stub_provider)
    goals = store.read("goals")
    # Either the template or the stub is acceptable
    assert "# Project Goals" in goals


def test_run_uses_template_when_available(tmp_path, stub_provider, monkeypatch):
    """When a template exists and no goals are supplied, the template is used."""
    monkeypatch.setattr("sys.stdin", io.StringIO(""))  # non-TTY stdin
    # Create a template file in the expected location
    template_dir = tmp_path / "project" / "templates"
    template_dir.mkdir(parents=True)
    template_content = "# My Template Goals\n\n- Template item\n"
    (template_dir / "01_goals.md").write_text(template_content, encoding="utf-8")
    template_store = ArtifactStore(base_dir=tmp_path)
    run(store=template_store, provider=stub_provider)
    goals = template_store.read("goals")
    assert "Template item" in goals
