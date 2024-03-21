/* eslint-disable no-console */
import { test, expect } from "@playwright/test";
import { setupEnvironment } from "../utils/environment";
import { loginUser } from "../utils/login";
import { bookRoundTrip } from "../utils/tripManagement";
import { handlePaymentFlow } from "../utils/payment";

setupEnvironment();

test.describe("Round Trip Booking Flow", () => {
  test.beforeEach(async ({ context }) => {
    console.log(`[*] Clearing browser cookies and site data`);
    await context.clearCookies();
  });

  test("Book a Round Trip", async ({ page }) => {
    await loginUser(page);
    await expect(page.getByText("Search for offers")).toBeVisible();
    await bookRoundTrip(page);
    await expect(page.getByRole("heading", { name: "Payment" })).toBeVisible();
    await handlePaymentFlow(page);
  });
});
