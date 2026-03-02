# Automation Testing Monorepo Demo

A practical demonstration of how to automate testing at every stage of the
Software Development Life Cycle (SDLC) using a JavaScript monorepo.

---

## What this repo demonstrates

| SDLC Stage | Practice | Where it lives |
|---|---|---|
| **Development** | Unit tests run locally before committing | `packages/*/` |
| **Code review** | CI runs on every pull request | `.github/workflows/ci.yml` |
| **Integration** | HTTP integration tests against the real Express app | `packages/api/__tests__/api.integration.test.js` |
| **Coverage gates** | 80 % threshold enforced via Jest | each `package.json` |
| **Multi-version testing** | Matrix over Node 18 & 20 | `.github/workflows/ci.yml` |
| **Artifact archival** | Coverage reports uploaded for every run | CI workflow |

---

## Monorepo structure

```
.
├── packages/
│   ├── utils/           # Shared math & string utilities
│   │   ├── src/
│   │   │   ├── math.js
│   │   │   ├── string.js
│   │   │   └── index.js
│   │   └── __tests__/
│   │       ├── math.test.js
│   │       └── string.test.js
│   └── api/             # Express TODO REST API
│       ├── src/
│       │   ├── app.js
│       │   ├── router.js
│       │   ├── todos.js
│       │   └── index.js
│       └── __tests__/
│           ├── todos.unit.test.js
│           └── api.integration.test.js
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions CI pipeline
└── package.json         # Root — npm workspaces config
```

---

## Getting started

### Prerequisites

- Node.js ≥ 18
- npm ≥ 9

### Install dependencies

```bash
npm install
```

### Run all tests (both packages)

```bash
npm test
```

### Run tests with coverage

```bash
npm run test:coverage
```

### Run tests for a single package

```bash
# utils package
cd packages/utils && npm test

# api package
cd packages/api && npm test
```

---

## Testing strategy

### Unit tests

Located in `__tests__/` next to each package's source code.  
They test individual functions in complete isolation — no network, no database.

```
packages/utils/__tests__/math.test.js    → add, subtract, multiply, divide, factorial
packages/utils/__tests__/string.test.js → capitalize, reverse, isPalindrome, truncate
packages/api/__tests__/todos.unit.test.js → in-memory CRUD store
```

### Integration tests

`packages/api/__tests__/api.integration.test.js` spins up the real Express
application in-process (using [supertest](https://github.com/ladjs/supertest))
and exercises the full HTTP request/response cycle end-to-end, including error
handling and HTTP status codes.

### Coverage gates

Each package enforces **80 % minimum coverage** (branches, functions, lines,
statements) via Jest's `coverageThreshold` setting.  The CI job fails if
coverage drops below that threshold, making coverage regressions visible in
pull requests.

---

## CI / CD pipeline

`.github/workflows/ci.yml` runs automatically on every push and pull request:

1. **Checkout** code
2. **Set up Node.js** (matrix: 18.x and 20.x)
3. **Install dependencies** with `npm ci` (reproducible, locked installs)
4. **Run utils tests** with coverage
5. **Run API tests** with coverage
6. **Upload coverage artifacts** for each Node version

This ensures that every change is validated before it can be merged.
