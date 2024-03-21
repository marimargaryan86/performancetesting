/* eslint-disable no-console */
import { Page } from "@playwright/test";
import { checkEnvironmentVariables } from "./environment";

export async function loginUser(page: Page): Promise<void> {
  console.log("[*] Logging user into dashboard...");
  console.log(`Page URL: ${page.url()}`);
  await page.goto("http://localhost:5173/login");
  checkEnvironmentVariables();

  await fillLoginForm(page);
  await handleCsrfToken(page);
}

export async function fillLoginForm(page: Page): Promise<void> {
  if (
    typeof process.env.E2E_USERNAME !== "string" ||
    typeof process.env.E2E_PASSWORD !== "string"
  ) {
    throw new Error("E2E_USERNAME or E2E_PASSWORD environment variables are not set.");
  }
  await page.getByPlaceholder("Enter E-Mail").click();
  await page.getByPlaceholder("Enter E-Mail").fill(process.env.E2E_USERNAME);
  await page.getByPlaceholder("Enter Password").click();
  await page.getByPlaceholder("Enter Password").fill(process.env.E2E_PASSWORD);
  await page.getByRole("button", { name: "Sign in" }).click();
}

export async function handleCsrfToken(page: Page): Promise<void> {
  await page.waitForLoadState();
  if (page.url().includes("csrf_token")) {
    console.log(`[*] 'csrf_token' found in URL. Clearing cookies and retrying login.`);
    await page.context().clearCookies();
    await page.reload();
    throw new Error("Clearing web browser cookies...");
  }
}
