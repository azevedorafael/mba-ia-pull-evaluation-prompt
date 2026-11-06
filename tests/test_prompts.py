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
    """The prompt must include six explicit input/output examples."""
    system_prompt = prompt_data["system_prompt"]
    assert system_prompt.count("Exemplo ") >= 6
    assert system_prompt.count("Entrada:") >= 6
    assert system_prompt.count("Saída:") >= 6


def test_prompt_distinguishes_technical_suggestions_from_facts(prompt_data):
    """Technical recommendations must be labeled rather than presented as facts."""
    system_prompt = prompt_data["system_prompt"]
    assert "Plano Técnico Sugerido" in system_prompt
    assert "sugestões a validar" in system_prompt
    assert "causa confirmada" in system_prompt


def test_prompt_preserves_complex_and_security_details(prompt_data):
    """Complex issues must retain relevant details without operational exploit steps."""
    system_prompt = prompt_data["system_prompt"]
    assert "por problema ou componente" in system_prompt
    assert "controles preventivos" in system_prompt
    assert "payloads operacionais" in system_prompt


def test_prompt_covers_dashboard_and_mobile_modal_edge_cases(prompt_data):
    """High-risk UI cases must cover filters, accessibility, and responsive details."""
    system_prompt = prompt_data["system_prompt"]
    assert "consistência entre o total e os registros exibidos" in system_prompt
    assert "foco no modal, tecla ESC e comportamento do backdrop" in system_prompt
    assert "Propostas a validar" in system_prompt


def test_prompt_preserves_complex_technical_plans_and_metrics(prompt_data):
    """Complex reports must retain architecture, phased tasks, and success metrics."""
    system_prompt = prompt_data["system_prompt"]
    assert "Tarefas Técnicas Sugeridas" in system_prompt
    assert "Métricas de Sucesso" in system_prompt
    assert "inventário de todos os requisitos" in system_prompt
    assert "valor atual → meta" in system_prompt


def test_prompt_history_contains_complete_snapshots():
    """Every archived prompt revision must contain a complete, loadable prompt."""
    history_dir = PROMPT_PATH.parent / "history"
    snapshots = sorted(
        history_dir.glob("bug_to_user_story_v2_iteration_*.yml"),
        key=lambda path: int(path.stem.rsplit("_", maxsplit=1)[1]),
    )

    assert len(snapshots) >= 5
    latest_snapshot = None
    for snapshot in snapshots:
        with snapshot.open(encoding="utf-8") as snapshot_file:
            data = yaml.safe_load(snapshot_file)
        assert data["bug_to_user_story_v2"]["system_prompt"].strip()
        latest_snapshot = data

    with PROMPT_PATH.open(encoding="utf-8") as prompt_file:
        active_prompt = yaml.safe_load(prompt_file)
    assert latest_snapshot == active_prompt


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
