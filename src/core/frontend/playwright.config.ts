/**
 * Playwright Configuration for E2E Tests
 *
 * Configures Playwright for end-to-end testing of the Next.js application.
 */

import { defineConfig, devices } from "@playwright/test";

/**
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: "./__tests__/e2e",

  /**
   * Maximum time one test can run for
   */
  timeout: 30 * 1000,

  /**
   * Run tests in files in parallel
   */
  fullyParallel: true,

  /**
   * Fail the build on CI if you accidentally left test.only in the source code
   */
  forbidOnly: !!process.env.CI,

  /**
   * Retry on CI only
   */
  retries: process.env.CI ? 2 : 0,

  /**
   * Opt out of parallel tests on CI
   */
  workers: process.env.CI ? 1 : undefined,

  /**
   * Reporter to use
   */
  reporter: "html",

  /**
   * Shared settings for all the projects below
   */
  use: {
    /**
     * Base URL to use in actions like `await page.goto('/')`
     */
    baseURL: "http://localhost:3000",

    /**
     * Collect trace when retrying the failed test
     */
    trace: "on-first-retry",

    /**
     * Screenshot on failure
     */
    screenshot: "only-on-failure",
  },

  /**
   * Configure projects for major browsers
   */
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  /**
   * Run your local dev server before starting the tests
   */
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
