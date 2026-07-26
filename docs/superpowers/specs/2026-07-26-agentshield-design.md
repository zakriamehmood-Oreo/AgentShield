# AgentShield — Design Spec

Date: 2026-07-26
Status: Approved

## 1. Purpose

AgentShield is an open-source, production-style platform that demonstrates
that AI-agent tool use can be observable, testable, permission-aware, and
subject to human approval. It monitors a synthetic e-commerce customer-support
agent, records its complete execution trace, evaluates its behavior against
deterministic and LLM-based criteria, and blocks unsafe tool calls (e.g. an
unauthorized refund driven by a prompt-injection payload hidden in order
notes) before they reach business systems.

The whole domain (customers, orders, policies) is synthetic — no proprietary
or employer data is used anywhere in the dataset or code.

## 2. Non-goals / explicit scope cuts

- No multi-user auth/login system for the dashboard. Cross-*tenant* (customer)
  data isolation is fully in scope and enforced by the gateway; operator
  identity for approvals is a simple name field recorded on the decision, not
  a full auth system.
- No third-party charting library — dashboard charts are hand-built with
  Tailwind/SVG.
- The "3-minute demo video" deliverable is a written outline/script, not an
  actual recorded video file.
- No GPU-based models anywhere; all model calls are hosted OpenAI, reached
  through an environment-configured model name.

## 3. Architecture

Four services, all runnable via Docker Compose:

- **`services/web`** — Next.js + TypeScript + Tailwind dashboard.
- **`services/api`** — FastAPI backend containing: the reference agent, the
  MCP security gateway, the eval engine, the attack simulator, the
  replay/regression CLI, and the human-approval API. Owns the primary
  Postgres connection for execution/trace data.
- **`services/tool_server`** — a FastMCP (official `mcp` Python SDK) server
  exposing the 7 mock business tools, backed by the same Postgres instance
  for the business-domain tables. Reachable only on the internal Docker
  network — never exposed to the dashboard or public internet.
- **PostgreSQL** — single instance, separate schemas/tables for business data
  vs. execution/trace data.
- **Pinecone (serverless)** — policy/knowledge retrieval index, populated by
  the seed script from `dataset/policies/`.

### Key security property

The agent has no client wired to `tool_server` directly. The gateway is
itself an MCP server (built with FastMCP) that the agent's tool-calling loop
talks to over real MCP — so from the agent's point of view, "the tools" *are*
the gateway. Internally, each gateway tool handler runs the full policy
pipeline (identity/authorization check, typed schema validation, monetary/
operational limits, untrusted-content labeling) *before* opening its own MCP
client connection to `tool_server` and forwarding the call. There is no code
path in `services/api` that reaches `tool_server` except through the gateway
module.

### Agent loop

1. Receive customer message (bound to a `conversation_id` and a
   `customer_id`, established via the demo harness / dashboard, never taken
   from free-text).
2. Retrieve relevant policy passages from Pinecone; record each retrieved
   passage (doc id, text, score) as a citation candidate.
3. Run an OpenAI tool-calling loop (Chat Completions API, tool list pulled
   dynamically from the gateway's `list_tools`), bounded by
   `AGENT_MAX_STEPS`. A repeated-identical-call detector forces early
   termination (cost/safety control against looping agents).
4. Return a structured response: message to customer, tools invoked with
   their gateway decisions, and policy citations actually used.

### Gateway decision pipeline (every tool call, both directions)

1. **Identity/authorization** — does the `customer_id` bound to this
   conversation match the ownership of the order/customer referenced in the
   tool arguments? Any mismatch is an automatic `BLOCK`
   (cross-customer-access defense).
2. **Schema validation** — typed pydantic models per tool for both request
   args and response payload; anything that doesn't validate is rejected
   before it reaches `tool_server` or the agent.
3. **Monetary/operational limits** — policy-driven numeric limits (e.g. max
   refund amount, max discount percent) evaluated against tool arguments.
4. **Untrusted-content labeling** — any text sourced from order notes, tool
   results, or other non-operator input is wrapped/tagged `untrusted` before
   it can influence subsequent agent reasoning or gateway decisions about
   *other* calls.
5. **Verdict** — `ALLOW`, `BLOCK`, or `REQUIRE_APPROVAL`, each carrying the
   specific policy/rule ID responsible, persisted alongside the call.

### Mock mode

`MOCK_MODE=true` swaps in a fake OpenAI client and fake Pinecone client
backed by recorded transcript fixtures (`services/api/tests/fixtures/`). This
is the default for the test suite and CI: the whole suite runs with zero
network calls and zero dollar cost. Real mode is opt-in via `.env`.

## 4. Repository structure

```
AgentShield/
├── services/
│   ├── api/
│   │   ├── agentshield/
│   │   │   ├── agent/           # OpenAI tool-calling loop, prompt versions
│   │   │   ├── gateway/         # MCP server: policy engine, verdicts
│   │   │   ├── retrieval/       # Pinecone client + citation logic
│   │   │   ├── eval/            # deterministic + LLM-judge evaluators
│   │   │   ├── attacks/         # attack scenario runner
│   │   │   ├── replay/          # regression CLI, threshold gate
│   │   │   ├── tracing/         # OTel-compatible spans, PII redaction
│   │   │   ├── db/              # SQLAlchemy models, session
│   │   │   ├── core/            # config, budgets, cache, mock-mode
│   │   │   └── api/             # FastAPI routers
│   │   ├── alembic/
│   │   └── tests/
│   ├── tool_server/
│   │   ├── agentshield_tools/
│   │   └── tests/
│   └── web/
├── dataset/
│   ├── scenarios/{normal,ambiguous,edge_cases,adversarial,authz_privacy}/*.yaml
│   └── policies/*.md
├── docs/
│   ├── architecture.md
│   ├── threat-model.md
│   ├── api.md
│   ├── demo-script.md
│   └── video-outline.md
├── scripts/                      # seed.py, eval.py, replay.py, run_attacks.py
├── .github/workflows/ci.yml
├── docker-compose.yml
├── .env.example
└── README.md
```

## 5. Data model

**Business domain** (owned/written by `tool_server`, read by gateway/agent):

- `customers`: id, `customer_key` (synthetic external id), `email_hash`,
  tier, created_at.
- `orders`: id, `customer_id` FK, order_number, status, total_amount,
  currency, items (JSON), `notes` (text — where indirect-injection payloads
  live), created_at.
- `shipments`: id, `order_id` FK, carrier, tracking_number, status, eta,
  history (JSON).
- `policies`: id, title, body, version, tags — source of truth; mirrored
  into Pinecone by the seed script.

**Execution & security** (owned by `api`):

- `conversations`: id, `customer_id` FK, `agent_version_id` FK, channel,
  status (`open` / `awaiting_approval` / `closed`), created_at.
- `messages`: id, `conversation_id` FK, role, content, created_at.
- `spans`: id, `conversation_id` FK, span_id, parent_span_id, name, kind
  (`llm_call` / `tool_call` / `retrieval` / `eval`), start/end time,
  attributes (JSON, PII-redacted before insert), status.
- `tool_calls`: id, `conversation_id` FK, `span_id` FK, tool_name, arguments
  (JSON), caller_identity, result (JSON), `decision`
  (`ALLOW`/`BLOCK`/`REQUIRE_APPROVAL`), `policy_id` FK, reasoning,
  monetary_impact, `contains_untrusted_content` (bool), created_at.
- `citations`: id, message_id FK, `policy_id` FK, passage, score.
- `approval_requests`: id, `tool_call_id` FK, status
  (`pending`/`approved`/`rejected`), reviewer, decision_reason, decided_at.
- `audit_log`: id, entity_type, entity_id, actor, action, payload (JSON),
  created_at, `prev_hash`, `hash` — append-only, hash-chained so tampering
  is detectable; this is the immutable record the approval interface writes
  to.

**Eval & versioning:**

- `agent_versions`: id, name, system_prompt, model_name, created_at.
- `scenarios`: DB mirror of the `dataset/scenarios/*.yaml` files (id,
  external_key, category, user_identity, customer_message, account_state,
  expected_action, allowed_tools, forbidden_actions,
  expected_policy_citations, requires_human_approval, version) — files are
  the source of truth; the table exists to join with results.
- `eval_runs`: id, dataset_version, `agent_version_id` FK, started_at,
  finished_at, config (JSON).
- `eval_results`: id, `eval_run_id` FK, `scenario_id` FK, metric_name,
  value, pass (bool), details (JSON).
- `regression_comparisons`: id, run_a_id, run_b_id, metric_name, value_a,
  value_b, delta, threshold, passed (bool) — what CI's regression gate reads.

## 6. Evaluation approach

Deterministic evaluators (no LLM call) wherever the answer can be computed
directly from the trace: task completion (did tool outcomes and final status
match the scenario's `expected_action`?), tool-selection accuracy, argument
correctness, policy compliance, unsafe-action rate, citation correctness,
retrieval hit-rate, attack-detection precision/recall, human-escalation
accuracy, latency/tokens/cost.

LLM-based judge reserved only for what genuinely requires semantic judgment:
hallucination (does the final response assert facts not supported by
retrieved policy or tool results?) and a qualitative task-completion-quality
score layered on top of the deterministic pass/fail. The judge model is
independently configurable via `OPENAI_EVAL_MODEL`.

## 7. Cost controls

`MAX_MODEL_CALLS_PER_RUN`, `MAX_CONCURRENCY` (semaphore), a per-run token/
dollar budget object that raises and gracefully stops a run when exceeded,
response caching keyed by (model, message-hash), dataset sampling
(`--sample N`), `MOCK_MODE` with transcript fixtures for CI, and
`AGENT_MAX_STEPS` plus a repeated-call detector to terminate looping agents.

## 8. Milestones

- **M0 — Foundations**: repo scaffold, Docker Compose, Alembic migrations,
  SQLAlchemy models, seed script, all 100 dataset scenarios + policy docs.
- **M1 — Core path**: `tool_server` (7 tools), gateway (full decision
  pipeline), reference agent (retrieval + citations + tool loop), tracing +
  redaction, mock-mode fakes + fixtures. This milestone alone makes the
  acceptance test runnable end-to-end.
- **M2 — Attack simulator + eval engine**: dataset runner, deterministic
  evaluators, the two LLM-judge evaluators, eval CLI report.
- **M3 — Replay/regression + human approval**: prompt/policy versioning,
  replay CLI with configurable regression thresholds, approval request
  lifecycle, hash-chained audit log, approval API.
- **M4 — Dashboard + docs/CI**: Next.js dashboard (overview, trace timeline,
  approvals queue, attacks, eval comparison), GitHub Actions (tests + secret
  scanning + regression gate), architecture diagram, threat model, API docs,
  demo script, video outline, README.

## 9. Acceptance criteria

1. `docker compose up` (with a filled-in `.env`) brings up db, tool_server,
   api, and web.
2. `python scripts/seed.py` populates Postgres and the Pinecone index from
   `dataset/`.
3. `pytest` passes end-to-end with `MOCK_MODE=true` and zero network calls.
4. **Literal acceptance test**: a seeded order's `notes` field contains a
   prompt-injection payload instructing the agent to issue an unauthorized
   refund. Running that scenario shows the agent attempting
   `request_refund`, the gateway returning `BLOCK` with a specific policy ID,
   and the dashboard's trace view for that conversation displaying: the
   original customer message, retrieved policy passages, the exact tool-call
   payload, the malicious note content flagged `untrusted`, the triggering
   policy/rule ID, the BLOCK decision, and the eval engine's verdict (attack
   detected = true).
5. `python scripts/replay.py` comparing a "safe" vs. deliberately weakened
   agent version demonstrates the regression gate failing when
   unsafe-action-rate or attack-detection-recall regresses past threshold.
