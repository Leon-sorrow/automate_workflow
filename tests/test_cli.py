"""Tests for the orchestrator CLI."""

from __future__ import annotations

import pytest

from orchestrator.cli import build_parser, main


def test_parser_requires_stage():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_parser_valid_stage():
    parser = build_parser()
    args = parser.parse_args(["--stage", "clarify"])
    assert args.stage == "clarify"


def test_parser_allow_stub_default():
    parser = build_parser()
    args = parser.parse_args(["--stage", "clarify"])
    assert args.allow_stub is True


def test_parser_no_allow_stub():
    parser = build_parser()
    args = parser.parse_args(["--stage", "clarify", "--no-allow-stub"])
    assert args.allow_stub is False


def test_parser_model_default():
    parser = build_parser()
    args = parser.parse_args(["--stage", "clarify"])
    assert args.model == "default"


def test_parser_goals_default():
    parser = build_parser()
    args = parser.parse_args(["--stage", "clarify"])
    assert args.goals == ""


def test_parser_goals_provided():
    parser = build_parser()
    args = parser.parse_args(["--stage", "clarify", "--goals", "Build a chat app"])
    assert args.goals == "Build a chat app"


def test_main_clarify_creates_goals_artifact(tmp_path, monkeypatch):
    """Running clarify stage (stub mode, no token) must create goals + requirements."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    main(["--stage", "clarify", "--allow-stub"])
    assert (tmp_path / "project" / "01_goals.md").exists()
    assert (tmp_path / "project" / "02_requirements.md").exists()


def test_main_clarify_uses_goals_arg(tmp_path, monkeypatch):
    """--goals argument should be written to project/01_goals.md."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    goals_text = "# My Goals\n\n- Build something great\n"
    main(["--stage", "clarify", "--allow-stub", "--goals", goals_text])
    goals_file = tmp_path / "project" / "01_goals.md"
    assert goals_file.exists()
    assert "Build something great" in goals_file.read_text()


def test_main_clarify_goals_arg_not_overwritten(tmp_path, monkeypatch):
    """--goals should not overwrite an existing non-empty project/01_goals.md."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    goals_file = tmp_path / "project" / "01_goals.md"
    goals_file.parent.mkdir(parents=True, exist_ok=True)
    goals_file.write_text("# Existing Goals\n", encoding="utf-8")
    main(["--stage", "clarify", "--allow-stub", "--goals", "New goals"])
    # The existing file should not be overwritten
    assert "Existing Goals" in goals_file.read_text()


def test_main_clarify_goals_arg_writes_when_empty_file(tmp_path, monkeypatch):
    """--goals should be used when project/01_goals.md is empty (treated as not set)."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    goals_file = tmp_path / "project" / "01_goals.md"
    goals_file.parent.mkdir(parents=True, exist_ok=True)
    goals_file.write_text("", encoding="utf-8")  # empty file → not "set"
    main(["--stage", "clarify", "--allow-stub", "--goals", "Build something new"])
    assert "Build something new" in goals_file.read_text()


def test_main_solutions_without_prerequisites_exits(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc_info:
        main(["--stage", "solutions"])
    assert exc_info.value.code == 1
