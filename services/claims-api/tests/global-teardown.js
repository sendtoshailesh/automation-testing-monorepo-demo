/**
 * Playwright global teardown – stop the Claims API server after all tests.
 */
'use strict';

module.exports = async function globalTeardown() {
  const pid = global.__CLAIMS_SERVER_PID__;
  if (pid) {
    try {
      process.kill(pid);
    } catch {
      // already gone
    }
  }
};
