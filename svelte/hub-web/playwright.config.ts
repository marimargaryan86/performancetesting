import { PlaywrightTestConfig, devices } from "@playwright/test";

const config: PlaywrightTestConfig = {
  // Specify the directory where your tests are located
  testDir: "./e2e-tests",

  // Configure projects for different browsers
  projects: [
    {
      // Project name, useful for reporting
      name: "Chromium",

      // Use the configurations of a desktop version of Chrome
      use: {
        ...devices["Desktop Chrome"],

        // Run tests in headed mode
        headless: false,

        // Base URL for the tests, so you don't need to repeat the full URL in the tests
        baseURL: "http://localhost:5173",
      },
    },
    // You can add more projects for different browsers if needed
  ],

  // Set up global test settings
  use: {
    // Any global settings you want to apply to all tests
  },

  // Configure the number of retries for failed tests. Useful in CI environments
  retries: 1,

  // Reporter to use. 'html' provides a visual report of the test results
  // reporter: 'html',

  // Additional configurations can be added here as needed
};

export default config;
