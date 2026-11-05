"""Publish optimized prompts to the LangSmith Prompt Hub."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from utils import check_env_vars, load_yaml, print_section_header

load_dotenv()

PROMPT_FILE = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "bug_to_user_story_v2.yml"
)


def validate_prompt(prompt_data: dict) -> tuple[bool, list[str]]:
    """Validate prompt content and metadata before publishing."""
    if not isinstance(prompt_data, dict):
        return False, ["Prompt data must be a mapping."]

    errors = []
    for field in ("description", "system_prompt", "user_prompt", "version"):
        value = prompt_data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string.")

    user_prompt = prompt_data.get("user_prompt")
    if isinstance(user_prompt, str) and "{bug_report}" not in user_prompt:
        errors.append("user_prompt must contain the {bug_report} variable.")

    techniques = prompt_data.get("techniques_applied")
    if not isinstance(techniques, list) or not all(
        isinstance(technique, str) and technique.strip()
        for technique in techniques
    ):
        errors.append("techniques_applied must be a list of non-empty strings.")
    elif len(techniques) < 2:
        errors.append("At least two prompt-engineering techniques are required.")

    tags = prompt_data.get("tags", [])
    if not isinstance(tags, list) or not all(
        isinstance(tag, str) and tag.strip() for tag in tags
    ):
        errors.append("tags must be a list of non-empty strings.")

    return not errors, errors


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """Publish a validated prompt to the public LangSmith Prompt Hub."""
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Prompt validation failed:")
        for error in errors:
            print(f"- {error}")
        return False

    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if not username:
        print("USERNAME_LANGSMITH_HUB is not configured.")
        return False

    try:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt_data["system_prompt"]),
                ("user", prompt_data["user_prompt"]),
            ]
        )
        techniques = prompt_data["techniques_applied"]
        description = (
            f"{prompt_data['description']}\n\n"
            f"Techniques applied: {', '.join(techniques)}"
        )
        tags = list(
            dict.fromkeys(
                [
                    *prompt_data.get("tags", []),
                    *[
                        technique.lower().replace(" ", "-")
                        for technique in techniques
                    ],
                ]
            )
        )
        hub_prompt_name = f"{username}/{prompt_name}"

        print(f"Publishing public prompt: {hub_prompt_name}")
        url = Client().push_prompt(
            hub_prompt_name,
            object=prompt,
            is_public=True,
            description=description,
            tags=tags,
        )
        print(f"Prompt published successfully: {url}")
        return True
    except Exception as error:
        print(f"Failed to publish prompt '{prompt_name}': {error}")
        return False


def main() -> int:
    """Load, validate, and publish the optimized prompt."""
    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    print_section_header("Publishing optimized prompt to LangSmith")
    prompts = load_yaml(str(PROMPT_FILE))
    if not isinstance(prompts, dict):
        print(f"Could not load prompt data from {PROMPT_FILE}.")
        return 1

    prompt_data = prompts.get("bug_to_user_story_v2")
    if not isinstance(prompt_data, dict):
        print(f"Prompt 'bug_to_user_story_v2' was not found in {PROMPT_FILE}.")
        return 1

    return (
        0
        if push_prompt_to_langsmith("bug_to_user_story_v2", prompt_data)
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
