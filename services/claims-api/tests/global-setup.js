/**
 * Playwright global setup – start the Claims API server before tests.
 * Used only when CLAIMS_API_URL is not set (i.e. no external server).
 */
'use strict';

const { spawn } = require('child_process');
const path = require('path');

async function waitForServer(url, maxMs = 10000) {
  const start = Date.now();
  while (Date.now() - start < maxMs) {
    try {
      const resp = await fetch(`${url}/health`);
      if (resp.ok) return;
    } catch {
      // not ready yet
    }
    await new Promise((r) => setTimeout(r, 200));
  }
  throw new Error(`Server at ${url} did not become ready within ${maxMs}ms`);
}

module.exports = async function globalSetup() {
  if (process.env.CLAIMS_API_URL) {
    // External server already running – nothing to start.
    return;
  }
  const serverPath = path.join(__dirname, '..', 'src', 'server.js');
  const serverProcess = spawn(process.execPath, [serverPath], {
    env: { ...process.env, PORT: '3000' },
    stdio: 'inherit',
  });
  global.__CLAIMS_SERVER_PID__ = serverProcess.pid;
  process.env.CLAIMS_API_URL = 'http://localhost:3000';
  await waitForServer('http://localhost:3000');
};
