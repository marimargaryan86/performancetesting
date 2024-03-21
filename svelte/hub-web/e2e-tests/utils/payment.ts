/* eslint-disable no-console */
import { Page } from "@playwright/test";

export async function handlePaymentFlow(page: Page): Promise<void> {
  await enterPassengerInformation(page);
  await enterContactInformation(page);

  await enterPaymentInformation(page);
  await page.getByRole("button", { name: "Book" }).click();
  await page.pause();
}

export async function enterPassengerInformation(page: Page): Promise<void> {
  await page.getByLabel("Title *").click();
  await page.getByText("Mr", { exact: true }).click();
  await page.getByPlaceholder("Enter first name").click();
  await page.getByPlaceholder("Enter first name").fill("John");
  await page.getByPlaceholder("Enter last name").click();
  await page.getByPlaceholder("Enter last name").fill("Doe");
  await page.getByPlaceholder("dd/mm/yyyy").click();
  await page.getByPlaceholder("dd/mm/yyyy").fill("01/02/1983");
  await page.getByLabel("Gender *").click();
  await page.getByText("Male", { exact: true }).click();
}

export async function enterContactInformation(page: Page): Promise<void> {
  await page.getByLabel("Country code *").click();
  await page.getByRole("listitem", { name: "United States (+1)" }).click();
  await page.getByPlaceholder("Enter phone number").click();
  await page.getByPlaceholder("Enter phone number").fill("9092151872");
  await page.getByPlaceholder("Enter email").click();
  await page.getByPlaceholder("Enter email").fill("test@snowfalltravel.com");

  await page.getByPlaceholder("Enter postcode").fill("29620");
  await page.getByPlaceholder("Enter address line 2").fill("Torremolinos");

  await page.getByPlaceholder("Enter city,").click();
  await page.getByPlaceholder("Enter city,").fill("Andalucia");
}

export async function enterPaymentInformation(page: Page): Promise<void> {
  console.log(`[*] Waiting for the Stripe iframes to load...`);

  // Use the first matching iframe for the card number assuming it's always the correct one.
  const cardNumberFrameLocator = page.frameLocator('iframe[name*="privateStripeFrame"]').nth(0);
  const cardNumberLocator = cardNumberFrameLocator
    .locator('[placeholder="1234 1234 1234 1234"]')
    .first();
  console.log(`[*] Entering card number...`);
  await cardNumberLocator.fill("4242 4242 4242 4242");
  // Use your test card details

  console.log(`[*] Waiting for the expiry date field to load within the iframe...`);
  // For the expiry date, assume it's in the same iframe as the card number.
  const expiryDateLocator = cardNumberFrameLocator.locator('[placeholder="MM / YY"]').first();
  await expiryDateLocator.click();
  await expiryDateLocator.fill("01 / 29");

  console.log(`[*] Waiting for the CVC field to load within the iframe...`);
  // For the CVC, we also assume it's in the same iframe as the card number.
  const cvcLocator = cardNumberFrameLocator.locator('[placeholder="CVC"]').first();
  await cvcLocator.fill("424");

  console.log(`[*] Waiting for the ZIP code field to load within the iframe...`);
  // For the ZIP code, assume it's in the same iframe as the card number if it's typically part of standard Stripe fields.
  const zipCodeLocator = cardNumberFrameLocator.locator('[placeholder="12345"]').first();
  await zipCodeLocator.click();
  await zipCodeLocator.fill("91764");
}
