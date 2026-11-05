"""Pull the challenge seed prompt from LangSmith Prompt Hub."""

import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langsmith import Client

from utils import check_env_vars, print_section_header, save_yaml

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "bug_to_user_story_v1.yml"
)


def pull_prompts_from_langsmith() -> bool:
    """Pull the seed prompt and save its system and user templates locally."""
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return False

    print_section_header("Pulling seed prompt from LangSmith")

    try:
        prompt = Client().pull_prompt(
            PROMPT_NAME,
            dangerously_pull_public_prompt=True,
        )

        message_templates: dict[str, list[str]] = {"system": [], "user": []}
        for message in prompt.messages:
            if isinstance(message, SystemMessagePromptTemplate):
                role = "system"
            elif isinstance(message, HumanMessagePromptTemplate):
                role = "user"
            else:
                raise ValueError(f"Unsupported prompt message: {message!r}")

            template = message.prompt.template
            if not isinstance(template, str):
                raise ValueError(f"Prompt message has no text template: {message!r}")
            message_templates[role].append(template)

        system_prompt = "\n\n".join(message_templates["system"]).strip()
        user_prompt = "\n\n".join(message_templates["user"]).strip()
        if not system_prompt or not user_prompt:
            raise ValueError("The pulled prompt must contain system and user messages.")

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Seed prompt pulled from LangSmith Prompt Hub.",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        if not save_yaml(prompt_data, str(OUTPUT_PATH)):
            return False

        print(f"Prompt saved to {OUTPUT_PATH}")
        return True
    except Exception as error:
        print(f"Failed to pull prompt '{PROMPT_NAME}': {error}")
        return False


def main() -> int:
    """Run the prompt pull workflow."""
    return 0 if pull_prompts_from_langsmith() else 1


if __name__ == "__main__":
    sys.exit(main())
