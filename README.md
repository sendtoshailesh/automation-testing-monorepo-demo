# automation-testing-monorepo-demo

A demo monorepo scaffold for test automation, covering unit tests, integration smoke tests, UI automation (Selenium), and API automation (Playwright).

## Repository Layout

```
.
├── .github/workflows/
│   ├── pr.yml           # PR checks: PII scan, per-service tests, evidence commit
│   └── nightly.yml      # Nightly full regression + release-evidence generation
├── docs/testing/
│   ├── standards.md     # Testing standards & conventions
│   └── baseline.md      # Quality baseline metrics
├── evidence/
│   └── templates/
│       ├── pr-evidence.md      # PR evidence Markdown template
│       └── release-evidence.md # Release evidence Markdown template
├── tools/ci/
│   ├── changed_services.py        # Detect which services changed in a PR
│   ├── pii_scan.py                # Scan test artefacts for PII leakage
│   ├── quarantine.py              # Manage quarantined (flaky) tests
│   ├── generate_pr_evidence.py    # Render PR evidence from template + test results
│   └── generate_release_evidence.py # Render release evidence
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

## CI

* **PR workflow** – runs on every pull-request: PII scan → per-service tests → generates and commits PR evidence.
* **Nightly workflow** – runs at 02:00 UTC on `main`: full regression across all services → generates release-evidence artefact.
