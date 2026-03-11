from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


class GlobalMemoryStore:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.projects_dir = repo_root / "memory" / "projects"
        self.lessons_dir = repo_root / "memory" / "lessons"
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.lessons_dir.mkdir(parents=True, exist_ok=True)

    def record_project(self, project: str, summary: str) -> Path:
        timestamp = datetime.now(timezone.utc).isoformat()
        path = self.projects_dir / f"{project}.md"
        body = f"# {project}\n\n- updated_at: {timestamp}\n- summary: {summary}\n"
        path.write_text(body, encoding="utf-8")
        return path

    def record_lesson(self, project: str, lesson: str) -> Path:
        timestamp = datetime.now(timezone.utc).isoformat()
        path = self.lessons_dir / f"{project}_lessons.md"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"- {timestamp}: {lesson}\n")
        return path
