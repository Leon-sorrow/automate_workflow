"""Tests for artifact store."""

from __future__ import annotations

import pytest

from orchestrator.artifacts import ArtifactStore


@pytest.fixture()
def store(tmp_path):
    return ArtifactStore(base_dir=tmp_path)


def test_exists_false_when_missing(store):
    assert store.exists("goals") is False


def test_write_and_exists(store):
    store.write("goals", "# Goals\n- Do something\n")
    assert store.exists("goals") is True


def test_write_and_read(store):
    content = "# Requirements\n- FR-01: something\n"
    store.write("requirements", content)
    assert store.read("requirements") == content


def test_read_missing_returns_empty(store):
    assert store.read("design") == ""


def test_exists_false_for_empty_file(store):
    # Write empty content
    path = store.path_for("plan")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    assert store.exists("plan") is False


def test_write_creates_parent_dirs(tmp_path):
    store = ArtifactStore(base_dir=tmp_path)
    store.write("goals", "content")
    assert (tmp_path / "project" / "01_goals.md").exists()


def test_path_for_returns_correct_path(store, tmp_path):
    path = store.path_for("human_checklist")
    assert "09_human_checklist.md" in str(path)
