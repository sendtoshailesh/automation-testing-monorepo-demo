// @ts-check
/**
 * Playwright API tests for the Claims API.
 *
 * The server is started as a global setup fixture before all tests.
 * Set CLAIMS_API_URL to point at an already-running server, or leave unset
 * to use the default http://localhost:3000 started below.
 */
const { test, expect } = require('@playwright/test');

// ── Helper ──────────────────────────────────────────────────────────────────

/**
 * @param {import('@playwright/test').APIRequestContext} request
 * @param {object} overrides
 */
async function createClaim(request, overrides = {}) {
  const body = { policy_id: 'POL-001', amount: 500, description: 'test claim', ...overrides };
  const resp = await request.post('/claims', { data: body });
  return resp;
}

// ── Health ───────────────────────────────────────────────────────────────────

test.describe('GET /health', () => {
  test('returns 200 and status ok', async ({ request }) => {
    const resp = await request.get('/health');
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.status).toBe('ok');
  });
});

// ── POST /claims ─────────────────────────────────────────────────────────────

test.describe('POST /claims', () => {
  test('creates a claim and returns 201', async ({ request }) => {
    const resp = await createClaim(request);
    expect(resp.status()).toBe(201);
    const claim = await resp.json();
    expect(claim.id).toBeTruthy();
    expect(claim.status).toBe('pending');
    expect(claim.policy_id).toBe('POL-001');
    expect(claim.amount).toBe(500);
  });

  test('missing policy_id returns 400', async ({ request }) => {
    const resp = await request.post('/claims', { data: { amount: 100 } });
    expect(resp.status()).toBe(400);
  });

  test('missing amount returns 400', async ({ request }) => {
    const resp = await request.post('/claims', { data: { policy_id: 'POL-001' } });
    expect(resp.status()).toBe(400);
  });

  test('zero amount returns 422', async ({ request }) => {
    const resp = await createClaim(request, { amount: 0 });
    expect(resp.status()).toBe(422);
  });
});

// ── GET /claims/:id ───────────────────────────────────────────────────────────

test.describe('GET /claims/:id', () => {
  test('returns the claim by id', async ({ request }) => {
    const created = await (await createClaim(request)).json();
    const resp = await request.get(`/claims/${created.id}`);
    expect(resp.status()).toBe(200);
    const claim = await resp.json();
    expect(claim.id).toBe(created.id);
  });

  test('unknown id returns 404', async ({ request }) => {
    const resp = await request.get('/claims/nonexistent-999');
    expect(resp.status()).toBe(404);
  });
});

// ── PATCH /claims/:id/status ─────────────────────────────────────────────────

test.describe('PATCH /claims/:id/status', () => {
  test('approves a claim', async ({ request }) => {
    const created = await (await createClaim(request)).json();
    const resp = await request.patch(`/claims/${created.id}/status`, {
      data: { status: 'approved' },
    });
    expect(resp.status()).toBe(200);
    expect((await resp.json()).status).toBe('approved');
  });

  test('invalid status returns 422', async ({ request }) => {
    const created = await (await createClaim(request)).json();
    const resp = await request.patch(`/claims/${created.id}/status`, {
      data: { status: 'unknown' },
    });
    expect(resp.status()).toBe(422);
  });
});
