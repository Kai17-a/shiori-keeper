import { defineConfig, devices } from "@playwright/test";

const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL ?? "http://127.0.0.1:8000";
const frontendBaseUrl =
  process.env.PLAYWRIGHT_FRONTEND_BASE_URL ?? "http://127.0.0.1:3000";

delete process.env.FORCE_COLOR;

export default defineConfig({
  testDir: "../tests/e2e",
  fullyParallel: false,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: frontendBaseUrl,
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
