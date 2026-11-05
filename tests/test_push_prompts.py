"""Tests for publishing optimized prompts to LangSmith."""

import sys
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import push_prompts


def valid_prompt_data():
    """Return a valid prompt suitable for push tests."""
    return {
        "description": "Converts bug reports into user stories.",
        "system_prompt": "You are a Product Owner.",
        "user_prompt": "Convert this report: {bug_report}",
        "version": "v2",
        "tags": ["bug-analysis"],
        "techniques_applied": ["Few-shot Learning", "Role Prompting"],
    }


def test_validate_prompt_requires_evaluation_input_variable():
    prompt_data = valid_prompt_data()
    prompt_data["user_prompt"] = "Convert this report."

    is_valid, errors = push_prompts.validate_prompt(prompt_data)

    assert not is_valid
    assert "user_prompt must contain the {bug_report} variable." in errors


def test_push_prompt_publishes_to_configured_public_handle(monkeypatch):
    client = Mock()
    client.push_prompt.return_value = "https://example.test/prompt"
    monkeypatch.setenv("USERNAME_LANGSMITH_HUB", "terminator")
    monkeypatch.setattr(push_prompts, "Client", Mock(return_value=client))

    result = push_prompts.push_prompt_to_langsmith(
        "bug_to_user_story_v2",
        valid_prompt_data(),
    )

    assert result
    args, kwargs = client.push_prompt.call_args
    assert args == ("terminator/bug_to_user_story_v2",)
    assert kwargs["is_public"] is True
    assert kwargs["object"].input_variables == ["bug_report"]
    assert kwargs["description"].endswith(
        "Techniques applied: Few-shot Learning, Role Prompting"
    )
    assert "few-shot-learning" in kwargs["tags"]


def test_push_prompt_rejects_invalid_prompt_without_publishing(monkeypatch):
    client = Mock()
    monkeypatch.setenv("USERNAME_LANGSMITH_HUB", "terminator")
    monkeypatch.setattr(push_prompts, "Client", Mock(return_value=client))
    prompt_data = valid_prompt_data()
    prompt_data["techniques_applied"] = []

    result = push_prompts.push_prompt_to_langsmith(
        "bug_to_user_story_v2",
        prompt_data,
    )

    assert not result
    client.push_prompt.assert_not_called()
