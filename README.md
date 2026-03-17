# automation-testing-monorepo-demo

A demo monorepo scaffold for test automation, covering unit tests, integration smoke tests, UI automation (Selenium), API automation (Playwright), and a **multi-agent SDLC testing pipeline** powered by GitHub Copilot custom agents.

## Repository Layout

```
.
├── .github/
│   ├── agents/                          # Custom agent definitions (multi-agent pipeline)
│   │   ├── test-orchestrator.md         # Central coordinator – routes triggers to sub-agents
│   │   ├── test-design.md               # Generates edge, boundary & negative test cases
│   │   ├── test-execution.md            # Runs Playwright / pytest / Selenium; collects artefacts
│   │   ├── validation-assertion.md      # Validates results vs baseline; schema & PII checks
│   │   ├── failure-analysis.md          # Triages failures; recommends fixes; quarantines flaky tests
│   │   └── reporting-feedback.md        # Generates evidence docs; logs bugs; emits CI status JSON
│   └── workflows/
│       ├── pr.yml                       # PR checks: PII scan, per-service tests, evidence commit
│       ├── nightly.yml                  # Nightly full regression + release-evidence generation
│       └── agent-test-pipeline.yml      # Agent-driven test pipeline (PR / manual / nightly)
├── docs/testing/
│   ├── standards.md     # Testing standards & conventions
│   └── baseline.md      # Quality baseline metrics
├── evidence/
│   └── templates/
│       ├── pr-evidence.md      # PR evidence Markdown template
│       └── release-evidence.md # Release evidence Markdown template
├── tools/
│   ├── agents/
│   │   └── session_state.py             # Shared JSON session store used by all pipeline agents
│   └── ci/
│       ├── changed_services.py          # Detect which services changed in a PR
│       ├── pii_scan.py                  # Scan test artefacts for PII leakage
│       ├── quarantine.py                # Manage quarantined (flaky) tests
│       ├── generate_pr_evidence.py      # Render PR evidence from template + test results
│       └── generate_release_evidence.py # Render release evidence
└── services/
    ├── pricing/    # Python · uv · pytest  (unit + integration smoke)
    ├── policy/     # Python · uv · pytest  (unit + integration smoke)
    ├── claims-api/ # Node · Playwright API tests
    └── ui-portal/  # Python · Selenium UI tests (self-hosted runner)
```

## Quick Start

### Python services (pricing / policy)

```bash
cd services/pricing
uv venv && uv pip install -e ".[dev]"
pytest tests/unit
# integration smoke (requires Docker)
docker compose up -d
pytest tests/integration
docker compose down
```

### Node claims-api

```bash
cd services/claims-api
npm ci
npx playwright install --with-deps
npm test
```

### Selenium ui-portal

```bash
cd services/ui-portal
uv venv && uv pip install -e ".[dev]"
pytest tests/
```

### Agent session state tool

The `tools/agents/session_state.py` utility is the shared memory store used by
all agents in the pipeline. You can also invoke it directly:

```bash
# Start a new session and capture the session ID
SESSION=$(python tools/agents/session_state.py new \
  --trigger manual \
  --services claims-api pricing \
  --sha "$(git rev-parse HEAD)")

# Write a result block (any agent does this after its step)
python tools/agents/session_state.py write \
  --session "$SESSION" \
  --key test_execution \
  --data '{"service":"claims-api","exit_code":0,"tests_run":9}'

# Read a block back
python tools/agents/session_state.py read --session "$SESSION" --key test_execution

# List all sessions
python tools/agents/session_state.py list

# Mark a session complete
python tools/agents/session_state.py complete --session "$SESSION" --status passed
```

Sessions are persisted in `agent-sessions.json` at the repository root
(committed back to the branch by the Reporting & Feedback Agent after each run).
The path can be overridden with the `AGENT_SESSION_FILE` environment variable.

## Multi-Agent Testing Framework

The repository ships a multi-agent SDLC testing pipeline inspired by the
architecture below. Five specialised agents are coordinated by a central
**Test Orchestrator Agent**:

```
          CI/CD Trigger      Manual Test Request     Business Requirements & Docs
               │                     │                          │
               └──────────┬──────────┘                         │
                           ▼                                    │
               ┌───────────────────────────┐                   │
               │   Test Orchestrator Agent  │◄──────────────────┘
               │  (Orchestration & State)   │
               └───┬───┬───┬───┬───┬───────┘
                   │   │   │   │   │
         ┌─────────┘   │   │   │   └──────────────────────┐
         ▼             ▼   │   ▼                           ▼
  ┌────────────┐ ┌──────────┐  │  ┌───────────────┐ ┌──────────────────┐
  │Test Design │ │   Test   │  │  │Failure Analysis│ │Reporting &       │
  │   Agent    │ │Execution │  │  │    Agent       │ │Feedback Agent    │
  └────────────┘ │  Agent   │  │  └───────────────┘ └──────────────────┘
                 └──────────┘  │
                               ▼
                    ┌─────────────────────┐
                    │Validation & Assertion│
                    │       Agent          │
                    └─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Session State &    │
                    │      Memory         │
                    └─────────────────────┘
```

### Agents

| Agent | File | Purpose |
|-------|------|---------|
| **Test Orchestrator** | `.github/agents/test-orchestrator.md` | Single entry point. Receives CI/CD, manual, or docs triggers; manages session lifecycle; sequences sub-agents. |
| **Test Design** | `.github/agents/test-design.md` | Generates edge-case, boundary, and negative tests for all services. Skips trivial getters and one-shot scripts. |
| **Test Execution** | `.github/agents/test-execution.md` | Runs Playwright (claims-api), pytest (pricing/policy), Selenium (ui-portal). Applies quarantine flags before each run. |
| **Validation & Assertion** | `.github/agents/validation-assertion.md` | Compares results against quality baseline; validates claims-api JSON schema; runs PII scan; detects flaky tests. |
| **Failure Analysis** | `.github/agents/failure-analysis.md` | Triages failures into `code_defect`, `test_defect`, `environment`, `flaky`, or `regression`; maps failures to source lines; recommends minimal fixes. |
| **Reporting & Feedback** | `.github/agents/reporting-feedback.md` | Renders PR/release evidence; opens GitHub issues for defects; emits structured JSON status for CI/CD. |

### When NOT to use agents

> The agents are designed for **non-trivial, context-dependent testing work**.
> Do not route the following through the agent pipeline:
>
> * ❌ Simple unit tests (covered by `pytest` / `playwright test` directly)
> * ❌ Basic smoke tests (a single happy-path call per endpoint)
> * ❌ Static validation checks (type-checking, linting)

## CI

* **PR workflow** (`pr.yml`) – runs on every pull-request: PII scan → per-service tests → generates and commits PR evidence.
* **Nightly workflow** (`nightly.yml`) – runs at 02:00 UTC on `main`: full regression across all services → generates release-evidence artefact.
* **Agent-driven pipeline** (`agent-test-pipeline.yml`) – orchestrates the multi-agent framework across three trigger modes:
  * **PR** – scoped to changed services; generates and commits PR evidence.
  * **Manual** (`workflow_dispatch`) – accepts an explicit service list.
  * **Nightly** – full regression at 03:00 UTC; generates release-evidence artefact (90-day retention).

  Job order: `orchestrate → test-design → execute (parallel per service) → validate → failure-analysis (on failure) → report`
