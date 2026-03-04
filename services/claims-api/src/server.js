/**
 * Claims API Express server (demo).
 */
'use strict';

const express = require('express');

const app = express();
app.use(express.json());

// In-memory store
const claims = new Map();
let nextId = 1;

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.get('/claims', (_req, res) => {
  res.json(Array.from(claims.values()));
});

app.post('/claims', (req, res) => {
  const { policy_id, amount, description } = req.body || {};
  if (!policy_id || amount == null) {
    return res.status(400).json({ error: 'policy_id and amount are required' });
  }
  if (typeof amount !== 'number' || amount <= 0) {
    return res.status(422).json({ error: 'amount must be a positive number' });
  }
  const id = String(nextId++);
  const claim = { id, policy_id, amount, description: description || '', status: 'pending' };
  claims.set(id, claim);
  return res.status(201).json(claim);
});

app.get('/claims/:id', (req, res) => {
  const claim = claims.get(req.params.id);
  if (!claim) {
    return res.status(404).json({ error: 'Claim not found' });
  }
  return res.json(claim);
});

app.patch('/claims/:id/status', (req, res) => {
  const claim = claims.get(req.params.id);
  if (!claim) {
    return res.status(404).json({ error: 'Claim not found' });
  }
  const { status } = req.body || {};
  const valid = ['pending', 'approved', 'rejected'];
  if (!valid.includes(status)) {
    return res.status(422).json({ error: `status must be one of: ${valid.join(', ')}` });
  }
  claim.status = status;
  return res.json(claim);
});

const PORT = process.env.PORT || 3000;

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Claims API listening on port ${PORT}`);
  });
}

module.exports = app;
