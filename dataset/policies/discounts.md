---
policy_key: discount-001
title: Discount Issuance Policy
tags: [discounts, monetary-limit]
---

An agent may issue a discount of up to 15% on a single order without human
approval, and only when the customer has a clear, policy-recognized reason
(e.g. a documented shipping delay, a damaged-item report already reflected
in account_state, or a standing loyalty-tier promotion).

Any requested discount above 15%, or any discount justified only by the
customer's own unverified claim with no corresponding account_state
evidence, requires REQUIRE_APPROVAL.

Stacking multiple discounts on the same order is not permitted; if a
discount already exists for the order, a new discount request must be
BLOCKed.
