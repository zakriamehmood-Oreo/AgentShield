"""Loads and validates every scenario YAML file under a dataset directory."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from agentshield.dataset.schema import ScenarioFile


def load_scenarios(dataset_dir: Path) -> list[ScenarioFile]:
    scenarios_root = Path(dataset_dir) / "scenarios"
    scenarios: list[ScenarioFile] = []
    for yaml_path in sorted(scenarios_root.glob("*/*.yaml")):
        raw = yaml.safe_load(yaml_path.read_text())
        try:
            scenarios.append(ScenarioFile(**raw))
        except ValidationError as exc:
            raise ValueError(f"Invalid scenario file {yaml_path}: {exc}") from exc
    return scenarios
