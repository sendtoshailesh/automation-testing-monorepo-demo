# Quality Baseline

This document records the established quality baselines for all services.  
Update this file whenever a baseline is officially revised.

---

## Baseline Metrics (v1.0 – initial scaffold)

| Service | Unit Tests | Unit Coverage | Integration Tests | Passing |
|---------|:----------:|:-------------:|:-----------------:|:-------:|
| pricing | 4 | ≥ 80 % | 2 | ✅ |
| policy | 4 | ≥ 80 % | 2 | ✅ |
| claims-api | 4 (Playwright API) | n/a | n/a | ✅ |
| ui-portal | 2 (Selenium) | n/a | n/a | ✅ |

---

## How to Update the Baseline

1. Run the full nightly suite against `main`.
2. Collect coverage reports from each service.
3. Update the table above and submit a PR with evidence attached.

---

## Regression Policy

* A PR may **not** reduce line coverage below the baseline for any service.
* If the baseline must be lowered for a legitimate reason (e.g. removing dead code), an explicit approval from the QA Lead is required and must be noted here.

---

## Flaky Test Tracking

| Test ID | Service | Quarantined | Tracking Issue | Target Fix Date |
|---------|---------|:-----------:|----------------|-----------------|
| _(none)_ | – | – | – | – |
