# Testing Standards

This document defines the testing standards and conventions for the monorepo.

---

## 1. Test Pyramid

```
         ▲
        /E2E\         ← slow, expensive, few
       /──────\
      / System \      ← integration smoke per service
     /──────────\
    /    Unit    \    ← fast, isolated, many
   ▼──────────────▼
```

| Layer | Location | Runner | Goal |
|-------|----------|--------|------|
| Unit | `tests/unit/` | pytest / Jest | ≥ 80 % line coverage |
| Integration smoke | `tests/integration/` | pytest + docker-compose | Happy-path & failure modes |
| API (contract) | `tests/` (claims-api) | Playwright | All REST endpoints respond correctly |
| UI (E2E smoke) | `tests/` (ui-portal) | Selenium | Critical user journeys |

---

## 2. Naming Conventions

### Python (pytest)

* Files: `test_<subject>.py`
* Functions: `test_<what>_<scenario>` (e.g. `test_calculate_premium_zero_age`)
* Classes: `Test<Subject>` (use only when grouping related scenarios)
* Fixtures: lowercase snake_case, scope should be the narrowest possible (`function` > `module` > `session`)

### Node / TypeScript (Playwright)

* Files: `<subject>.spec.ts`
* Describe blocks: plain English describing the endpoint or feature
* Test names: `<HTTP method> <path> – <scenario>` (e.g. `POST /claims – missing body returns 400`)

---

## 3. Assertions

* Prefer explicit assertions over broad catch-alls.
* One logical assertion per test (multiple `assert` statements are fine if they all test the same behaviour).
* Never `assert True` or `assert False` without a message.

---

## 4. Test Data

* All test data must be synthetic – no production PII.
* Use factories or fixtures to generate data; avoid hard-coded magic strings.
* Database state must be reset between integration tests (use transactions that roll back, or fresh containers via docker-compose).

---

## 5. Flaky Tests

* A test that fails intermittently **must** be quarantined within one business day using `tools/ci/quarantine.py`.
* Quarantined tests must have an associated tracking issue.
* Quarantined tests must be fixed or deleted within 2 sprint cycles.

---

## 6. Coverage Requirements

| Service | Unit coverage | Integration smoke |
|---------|:-------------:|:-----------------:|
| pricing | ≥ 80 % | required |
| policy | ≥ 80 % | required |
| claims-api | ≥ 70 % | required |
| ui-portal | n/a | required |

---

## 7. CI Rules

* PRs must pass all tests before merging.
* PII scan must pass.
* PR evidence must be generated and committed.
* Self-hosted Selenium tests are *advisory* for PRs (not blocking) but **mandatory** for nightly.
