"""Pydantic schema for a single scenario YAML file under dataset/scenarios/.

The YAML files are the source of truth for the dataset; this schema is
what both the seed script (loads them into the `scenarios` table) and the
eval engine (reads expected_action/forbidden_actions/etc. to grade a run)
depend on.
"""

from typing import Literal

from pydantic import BaseModel

Category = Literal["normal", "ambiguous", "edge_case", "adversarial", "authz_privacy"]


class ScenarioFile(BaseModel):
    external_key: str
    category: Category
    user_identity: dict
    customer_message: str
    account_state: dict
    expected_action: str
    allowed_tools: list[str]
    forbidden_actions: list[str]
    expected_policy_citations: list[str]
    requires_human_approval: bool
    version: int = 1
