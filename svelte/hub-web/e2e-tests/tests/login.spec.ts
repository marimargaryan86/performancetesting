/* eslint-disable no-console */
import { test, expect } from "@playwright/test";
import { setupEnvironment } from "../utils/environment";
import { loginUser } from "../utils/login";

setupEnvironment();

test.describe("Authentication Flow", () => {
  test.beforeEach(async ({ context }) => {
    console.log(`[*] Clearing browser cookies and site data`);
    await context.clearCookies();
  });

  test("Enter credentials for a user to login", async ({ page }) => {
    await loginUser(page);
    await expect(page.getByText("Search for offers")).toBeVisible();
  });
});
