from pathlib import Path

from agentshield.dataset.loader import load_scenarios

DATASET_DIR = Path(__file__).resolve().parents[3] / "dataset"

EXPECTED_COUNTS = {
    "normal": 30,
    "ambiguous": 20,
    "edge_case": 20,
    "adversarial": 20,
    "authz_privacy": 10,
}


def test_dataset_has_exactly_100_scenarios_with_expected_category_counts():
    scenarios = load_scenarios(DATASET_DIR)
    assert len(scenarios) == 100

    counts_by_category: dict[str, int] = {}
    for scenario in scenarios:
        counts_by_category[scenario.category] = counts_by_category.get(scenario.category, 0) + 1

    assert counts_by_category == EXPECTED_COUNTS


def test_all_external_keys_are_unique():
    scenarios = load_scenarios(DATASET_DIR)
    keys = [s.external_key for s in scenarios]
    assert len(keys) == len(set(keys))


def test_acceptance_test_scenario_is_present_and_shaped_correctly():
    scenarios = load_scenarios(DATASET_DIR)
    matches = [s for s in scenarios if s.external_key == "adversarial-003"]
    assert len(matches) == 1
    scenario = matches[0]
    assert "request_refund" in scenario.forbidden_actions
    assert "refund-001" in scenario.expected_policy_citations
    assert "order_notes" in scenario.account_state
    assert "ignore" in scenario.account_state["order_notes"].lower()


def test_all_policy_docs_exist():
    policies_dir = DATASET_DIR / "policies"
    expected_files = {"refunds.md", "shipping.md", "discounts.md", "privacy.md", "escalation.md"}
    actual_files = {p.name for p in policies_dir.glob("*.md")}
    assert expected_files.issubset(actual_files)
