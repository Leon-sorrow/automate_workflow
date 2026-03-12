"""Read and write project artifact Markdown files."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_DIR = Path("project")

ARTIFACT_FILES = {
    "goals": PROJECT_DIR / "01_goals.md",
    "requirements": PROJECT_DIR / "02_requirements.md",
    "solution_options": PROJECT_DIR / "03_solution_options.md",
    "design": PROJECT_DIR / "04_design.md",
    "plan": PROJECT_DIR / "05_plan.md",
    "verification": PROJECT_DIR / "07_verification.md",
    "review": PROJECT_DIR / "08_review.md",
    "human_checklist": PROJECT_DIR / "09_human_checklist.md",
}

TEMPLATE_DIR = PROJECT_DIR / "templates"


class ArtifactStore:
    """Simple file-based store for project artifacts."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        if base_dir is not None:
            self._base = Path(base_dir)
            self._artifact_files = {
                key: self._base / path for key, path in ARTIFACT_FILES.items()
            }
        else:
            self._base = Path(os.getcwd())
            self._artifact_files = {
                key: self._base / path for key, path in ARTIFACT_FILES.items()
            }

    def exists(self, artifact: str) -> bool:
        """Return True if the artifact file exists and is non-empty."""
        path = self._artifact_files[artifact]
        return path.exists() and path.stat().st_size > 0

    def read(self, artifact: str) -> str:
        """Read artifact content; return empty string if missing."""
        path = self._artifact_files[artifact]
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def write(self, artifact: str, content: str) -> None:
        """Write content to an artifact file, creating parent dirs as needed."""
        path = self._artifact_files[artifact]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"[artifacts] Written: {path}")

    def read_template(self, name: str) -> str:
        """Read a template file from project/templates/."""
        template_path = self._base / TEMPLATE_DIR / f"{name}.md"
        if not template_path.exists():
            return ""
        return template_path.read_text(encoding="utf-8")

    def path_for(self, artifact: str) -> Path:
        """Return the Path for the given artifact key."""
        return self._artifact_files[artifact]
