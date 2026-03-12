"""Tests for the GitHub Models LLM provider stub behaviour."""

from __future__ import annotations

import pytest

from orchestrator.llm.github_models import DEFAULT_MODEL, GitHubModelsProvider


def test_stub_returned_when_no_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    provider = GitHubModelsProvider(allow_stub=True)
    result = provider.complete("sys", "user prompt")
    assert "[STUB]" in result


def test_no_stub_raises_when_not_allowed(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    provider = GitHubModelsProvider(allow_stub=False)

    with pytest.raises(RuntimeError, match="allow_stub=False"):
        provider.complete("sys", "user prompt")


def test_default_model_resolution():
    provider = GitHubModelsProvider(model="default")
    assert provider.model == DEFAULT_MODEL


def test_custom_model_preserved():
    provider = GitHubModelsProvider(model="gpt-4o")
    assert provider.model == "gpt-4o"
