# Release Test Evidence – Nightly Run {{RUN_ID}}

| Field | Value |
|-------|-------|
| **Run ID** | {{RUN_ID}} |
| **Commit SHA** | `{{SHA}}` |
| **Generated** | {{TIMESTAMP}} |
| **Overall Status** | {{OVERALL_STATUS}} |

---

## Summary

| Metric | Count |
|--------|------:|
| Total tests run | {{TOTAL_TESTS}} |
| Failures | {{TOTAL_FAILURES}} |
| Errors | {{TOTAL_ERRORS}} |
| Skipped | {{TOTAL_SKIPPED}} |

---

## Detailed Results

{{TEST_RESULTS_TABLE}}

---

## Release Criteria

- [ ] All unit tests pass (0 failures, 0 errors)
- [ ] All integration smoke tests pass
- [ ] No PII / secrets detected in artefacts
- [ ] Playwright API tests pass
- [ ] Selenium UI smoke tests pass (self-hosted)

---

## Approvals

| Role | Name | Date |
|------|------|------|
| QA Lead | | |
| Release Manager | | |
| Security Review | | |

---

_This document was generated automatically by the nightly workflow.  
Do not edit manually — re-run the workflow to regenerate._
