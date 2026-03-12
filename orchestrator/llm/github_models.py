"""GitHub Models LLM provider.

Uses the GitHub Models inference API with the ``GITHUB_TOKEN`` environment
variable for authentication.  Falls back to deterministic stub content when
the call fails and ``allow_stub=True``.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from orchestrator.llm.base import LLMProvider

GITHUB_MODELS_ENDPOINT = "https://models.inference.ai.azure.com"
DEFAULT_MODEL = "gpt-4o-mini"


class GitHubModelsProvider(LLMProvider):
    """Call GitHub Models (Azure-backed) inference API.

    Parameters
    ----------
    model:
        Model name to use.  ``"default"`` resolves to ``DEFAULT_MODEL``.
    allow_stub:
        When *True* and the API call fails, return stub content instead of
        raising an exception.
    """

    def __init__(self, model: str = "default", allow_stub: bool = True) -> None:
        self.model = DEFAULT_MODEL if model == "default" else model
        self.allow_stub = allow_stub

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return completion from GitHub Models or a stub on failure."""
        token = os.environ.get("GITHUB_TOKEN", "")
        if not token:
            reason = "GITHUB_TOKEN not set"
            if self.allow_stub:
                return self._stub(user_prompt, reason=reason)
            raise RuntimeError(f"LLM call failed and allow_stub=False: {reason}")

        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 4096,
            }
        ).encode()

        req = urllib.request.Request(  # noqa: S310 - HTTPS-only endpoint
            f"{GITHUB_MODELS_ENDPOINT}/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 - HTTPS only
                body = json.loads(resp.read().decode())
                return body["choices"][0]["message"]["content"]
        except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
            reason = str(exc)
            print(f"[llm] GitHub Models call failed: {reason}", file=sys.stderr)
            if self.allow_stub:
                return self._stub(user_prompt, reason=reason)
            raise RuntimeError(f"LLM call failed and allow_stub=False: {reason}") from exc

    @staticmethod
    def _stub(user_prompt: str, reason: str = "") -> str:
        """Return deterministic stub content."""
        note = f"<!-- stub: {reason} -->" if reason else "<!-- stub -->"
        preview = user_prompt[:120].replace("\n", " ")
        return (
            f"{note}\n\n"
            "**[STUB]** LLM response unavailable. "
            "Please fill in this section manually.\n\n"
            f"_Prompt preview: {preview}_\n"
        )
