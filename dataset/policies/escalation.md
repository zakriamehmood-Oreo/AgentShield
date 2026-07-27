---
policy_key: escalation-001
title: Human Escalation Policy
tags: [escalation, human-approval]
---

An agent must escalate to a human (via escalate_to_human) rather than
resolve the request itself when: the customer explicitly asks for a human,
the customer expresses significant frustration or distress, the requested
action would require REQUIRE_APPROVAL from the gateway and the customer
declines to wait, or the agent cannot determine a safe action after
retrieving relevant policy.

An agent must never attempt to talk a customer out of escalating, and must
never fabricate a resolution to avoid escalating.
