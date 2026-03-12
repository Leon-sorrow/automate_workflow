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


def test_main_clarify_creates_goals_artifact(tmp_path, monkeypatch):
    """Running clarify stage (stub mode, no token) must create goals + requirements."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    main(["--stage", "clarify", "--allow-stub"])
    assert (tmp_path / "project" / "01_goals.md").exists()
    assert (tmp_path / "project" / "02_requirements.md").exists()


def test_main_solutions_without_prerequisites_exits(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc_info:
        main(["--stage", "solutions"])
    assert exc_info.value.code == 1
