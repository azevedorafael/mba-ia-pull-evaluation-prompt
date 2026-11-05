"""Automated validation tests for optimized prompts."""

from pathlib import Path

import pytest
import yaml

PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "bug_to_user_story_v2.yml"
)


@pytest.fixture(scope="module")
def prompt_data():
    """Load the optimized prompt from YAML."""
    with PROMPT_PATH.open(encoding="utf-8") as prompt_file:
        data = yaml.safe_load(prompt_file)
    return data["bug_to_user_story_v2"]


def test_prompt_has_system_prompt(prompt_data):
    """The optimized prompt must define a non-empty system message."""
    assert prompt_data["system_prompt"].strip()


def test_prompt_has_role_definition(prompt_data):
    """The system message must define the assistant's role."""
    assert "Você é um Product Owner" in prompt_data["system_prompt"]


def test_prompt_mentions_format(prompt_data):
    """The prompt must require Markdown and a standard user story structure."""
    system_prompt = prompt_data["system_prompt"]
    assert "Markdown" in system_prompt
    assert "Como [persona], eu quero [necessidade], para que [benefício]" in system_prompt


def test_prompt_has_few_shot_examples(prompt_data):
    """The prompt must include at least two explicit input/output examples."""
    system_prompt = prompt_data["system_prompt"]
    assert system_prompt.count("Exemplo ") >= 2
    assert system_prompt.count("Entrada:") >= 2
    assert system_prompt.count("Saída:") >= 2


def test_prompt_no_todos(prompt_data):
    """No unfinished TODO markers may remain in the prompt."""
    serialized_prompt = yaml.safe_dump(prompt_data, allow_unicode=True)
    assert "[TODO]" not in serialized_prompt
    assert "TODO" not in serialized_prompt


def test_minimum_techniques(prompt_data):
    """At least two prompt-engineering techniques must be documented."""
    techniques = prompt_data.get("techniques_applied", [])
    assert len(techniques) >= 2
    assert all(technique.strip() for technique in techniques)
