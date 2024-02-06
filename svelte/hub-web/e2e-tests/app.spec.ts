/* eslint-disable no-console */
import { test, Page } from "@playwright/test";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const setupEnvironment = (): void => {
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  dotenv.config({ path: path.join(__dirname, "../.env") });
};

setupEnvironment();

test.describe("Trip booking flow", () => {
  test.beforeEach(async ({ context }) => {
    console.log(`[*] Clearing browser cookies and site data`);
    await context.clearCookies();
  });

  test("Search for trip offers", async ({ page }) => {
    await loginUser(page);
    await searchForTrip(page);
    await page.pause();
  });
});

async function loginUser(page: Page): Promise<void> {
  console.log("[*] Logging user into dashboard...");
  console.log(`Page URL: ${page.url()}`);
  await page.goto("http://localhost:5173/login");
  checkEnvironmentVariables();

  await fillLoginForm(page);
  await handleCsrfToken(page);
}

function checkEnvironmentVariables(): void {
  if (!process.env.USERNAME || !process.env.PASSWORD) {
    console.error(
      "ERROR: USERNAME and PASSWORD environment variables are not set. Please set them in your .env file.",
    );
    throw new Error("Missing USERNAME or PASSWORD environment variables");
  }
}
async function fillLoginForm(page: Page): Promise<void> {
  if (typeof process.env.USERNAME !== "string" || typeof process.env.PASSWORD !== "string") {
    throw new Error("USERNAME or PASSWORD environment variables are not set.");
  }
  await page.getByPlaceholder("Enter E-Mail").click();
  await page.getByPlaceholder("Enter E-Mail").fill(process.env.USERNAME);
  await page.getByPlaceholder("Enter Password").click();
  await page.getByPlaceholder("Enter Password").fill(process.env.PASSWORD);
  await page.getByRole("button", { name: "Sign in" }).click();
}

async function handleCsrfToken(page: Page): Promise<void> {
  await page.waitForLoadState();
  if (page.url().includes("csrf_token")) {
    console.log(`[*] 'csrf_token' found in URL. Clearing cookies and retrying login.`);
    await page.context().clearCookies();
    await page.reload();
    throw new Error("Clearing web browser cookies...");
  }
}

async function searchForTrip(page: Page): Promise<void> {
  await page.waitForURL("**/trip-management/book");
  console.log(`[*] Entering trip details...`);

  // Fill trip details
  await fillTripDetails(page);

  // Trigger the search action
  await page.locator("button:nth-child(5)").first().click();
  console.log(`[*] Searching for trip...`);
  await waitForPostRequest(page);
}

async function fillTripDetails(page: Page): Promise<void> {
  await page.getByLabel("From *").click();
  await page.getByLabel("From *").fill("Salzburg Hauptbahnhof");
  await page.getByText("Salzburg Hauptbahnhof (S-Bahn").click();
  await page.getByLabel("To *").click();
  await page.getByLabel("To *").fill("Munich Central Station");
  await page.getByText("Munich Central Station,").click();
  await page.getByLabel("Open date picker").click();
  await page.getByLabel("Thursday, 29 February").click();
}

async function waitForPostRequest(page: Page): Promise<void> {
  try {
    await page.waitForRequest(
      (request) =>
        request.method() === "POST" &&
        request.url() === "http://localhost:5173/integration/trip-management?action=getOffers",
      { timeout: 10000 },
    );
    console.log(`[*] POST request to get offers detected.`);
  } catch (e) {
    console.log(`[*] POST request to get offers not detected. Retrying search...`);
    await page.getByText("Book now").click();
  }

  await page.waitForLoadState("domcontentloaded");
  console.log(`DOM Content Loaded`);

  await page
    .waitForURL("http://localhost:5173/trip-management/book/payment")
    .then(() => console.log(`[*] Navigated to ${page.url()}...`));
}
