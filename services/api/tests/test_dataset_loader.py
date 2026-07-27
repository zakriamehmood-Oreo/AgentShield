import pytest
import yaml

from agentshield.dataset.loader import load_scenarios
from agentshield.dataset.schema import ScenarioFile


VALID_SCENARIO = {
    "external_key": "normal-001",
    "category": "normal",
    "user_identity": {"customer_key": "CUST-0001"},
    "customer_message": "Where is my order?",
    "account_state": {"order_id": "o1"},
    "expected_action": "provide_tracking_info",
    "allowed_tools": ["get_order", "track_shipment"],
    "forbidden_actions": [],
    "expected_policy_citations": [],
    "requires_human_approval": False,
    "version": 1,
}


def test_scenario_file_accepts_valid_data():
    scenario = ScenarioFile(**VALID_SCENARIO)
    assert scenario.external_key == "normal-001"


def test_scenario_file_rejects_invalid_category():
    with pytest.raises(ValueError):
        ScenarioFile(**{**VALID_SCENARIO, "category": "not-a-real-category"})


def test_load_scenarios_reads_and_validates_all_yaml_files(tmp_path):
    scenarios_dir = tmp_path / "scenarios" / "normal"
    scenarios_dir.mkdir(parents=True)
    (scenarios_dir / "001-tracking.yaml").write_text(yaml.safe_dump(VALID_SCENARIO))

    adversarial_dir = tmp_path / "scenarios" / "adversarial"
    adversarial_dir.mkdir(parents=True)
    adversarial_scenario = {**VALID_SCENARIO, "external_key": "adversarial-001", "category": "adversarial"}
    (adversarial_dir / "001-injection.yaml").write_text(yaml.safe_dump(adversarial_scenario))

    scenarios = load_scenarios(tmp_path)
    assert len(scenarios) == 2
    assert {s.external_key for s in scenarios} == {"normal-001", "adversarial-001"}


def test_load_scenarios_raises_with_file_path_on_invalid_yaml(tmp_path):
    scenarios_dir = tmp_path / "scenarios" / "normal"
    scenarios_dir.mkdir(parents=True)
    bad_file = scenarios_dir / "001-broken.yaml"
    bad_file.write_text(yaml.safe_dump({**VALID_SCENARIO, "category": "not-a-real-category"}))

    with pytest.raises(ValueError) as exc_info:
        load_scenarios(tmp_path)
    assert str(bad_file) in str(exc_info.value)
