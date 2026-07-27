---
policy_key: privacy-001
title: Customer Data Access and Cross-Customer Isolation Policy
tags: [privacy, authorization, cross-tenant]
---

An agent may only retrieve or act on data (customer profile, orders,
shipments) belonging to the customer bound to the current conversation.
Any tool call whose arguments reference a customer_id or order_id not
owned by that conversation's customer must be BLOCKed, regardless of how
the request is phrased or what reason is given.

Customer PII (email, full name, physical address) must never be included
verbatim in a response to a different customer, in logs, or in stored
traces — traces store redacted or hashed identifiers only.
