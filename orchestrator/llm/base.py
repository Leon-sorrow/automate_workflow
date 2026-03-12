"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interface for LLM providers used by the orchestrator."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return a text completion for the given prompts.

        Parameters
        ----------
        system_prompt:
            Instructions/context for the model.
        user_prompt:
            The user/task message.

        Returns
        -------
        str
            The model's response text.
        """
