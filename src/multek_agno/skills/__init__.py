"""Bundled skills for Agno agents."""

from __future__ import annotations

import importlib.resources
from pathlib import Path
from typing import Optional

from agno.skills.agent_skills import Skills
from agno.skills.loaders.base import SkillLoader
from agno.skills.loaders.local import LocalSkills


def get_bundled_skills_path() -> Path:
    """Return the filesystem path to the bundled skills directory."""
    return Path(str(importlib.resources.files("multek_agno.skills") / "_bundled"))


def load_skills(
    include: Optional[list[str]] = None,
    extra_loaders: Optional[list[SkillLoader]] = None,
) -> Skills:
    """Load bundled skills and return a configured ``Skills`` instance.

    Args:
        include: If provided, only load the named bundled skills.
            Raises ``FileNotFoundError`` for unknown skill names.
        extra_loaders: Additional ``SkillLoader`` instances to combine
            with the bundled skills.

    Returns:
        An ``agno.skills.agent_skills.Skills`` instance ready to attach
        to an ``Agent``.
    """
    bundled_path = get_bundled_skills_path()
    loaders: list[SkillLoader] = []

    if include is not None:
        for name in include:
            skill_dir = bundled_path / name
            if not skill_dir.is_dir():
                available = [p.name for p in bundled_path.iterdir() if p.is_dir() and not p.name.startswith("__")]
                raise FileNotFoundError(f"Bundled skill '{name}' not found. Available: {available}")
            loaders.append(LocalSkills(str(skill_dir)))
    else:
        loaders.append(LocalSkills(str(bundled_path)))

    if extra_loaders:
        loaders.extend(extra_loaders)

    return Skills(loaders=loaders)


__all__ = ["get_bundled_skills_path", "load_skills"]
