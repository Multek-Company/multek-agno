"""Tests for the bundled skills module."""

from pathlib import Path

import pytest
from agno.skills.agent_skills import Skills
from agno.skills.loaders.local import LocalSkills
from agno.tools.function import Function

from multek_agno.skills import get_bundled_skills_path, load_skills

EXPECTED_SKILLS = {"visualizer", "data-analysis"}


def test_get_bundled_skills_path_exists() -> None:
    path = get_bundled_skills_path()
    assert path.is_dir(), f"Bundled skills path does not exist: {path}"


def test_bundled_path_contains_expected_skills() -> None:
    path = get_bundled_skills_path()
    subdirs = {p.name for p in path.iterdir() if p.is_dir() and not p.name.startswith("__")}
    assert EXPECTED_SKILLS.issubset(subdirs), f"Missing skills: {EXPECTED_SKILLS - subdirs}"


def test_load_skills_returns_skills_instance() -> None:
    skills = load_skills()
    assert isinstance(skills, Skills)


def test_load_skills_loads_all_bundled() -> None:
    skills = load_skills()
    names = set(skills.get_skill_names())
    assert EXPECTED_SKILLS == names


def test_load_skills_include_filter() -> None:
    skills = load_skills(include=["visualizer"])
    names = skills.get_skill_names()
    assert names == ["visualizer"]


def test_load_skills_invalid_name_raises() -> None:
    with pytest.raises(FileNotFoundError, match="nonexistent"):
        load_skills(include=["nonexistent"])


def test_load_skills_with_extra_loaders(tmp_path: Path) -> None:
    # Create a minimal extra skill
    skill_dir = tmp_path / "extra-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: extra-skill\ndescription: An extra skill for testing\n---\n\nExtra skill instructions.\n"
    )

    extra_loader = LocalSkills(str(tmp_path))
    skills = load_skills(extra_loaders=[extra_loader])
    names = set(skills.get_skill_names())
    assert "extra-skill" in names
    assert EXPECTED_SKILLS.issubset(names)


def test_bundled_skills_have_valid_metadata() -> None:
    skills = load_skills()
    for skill in skills.get_all_skills():
        assert skill.name, f"Skill has empty name: {skill}"
        assert skill.description, f"Skill '{skill.name}' has empty description"
        assert skill.instructions, f"Skill '{skill.name}' has empty instructions"


def test_skills_get_tools() -> None:
    skills = load_skills()
    tools = skills.get_tools()
    assert len(tools) == 3
    assert all(isinstance(t, Function) for t in tools)
