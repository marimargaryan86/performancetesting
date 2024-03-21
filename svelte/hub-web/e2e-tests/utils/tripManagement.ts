/* eslint-disable no-console */
import { Page } from "@playwright/test";

export async function bookOneWayTrip(page: Page): Promise<void> {
  console.log(`[*] Entering origin and destination for one-way trip...`);
  await page.waitForURL("**/trip-management/book/rail");
  await checkIfRoundTripEnabled(page);
  await selectOneWayTripOption(page);
  await enterOriginDestination(page);
  await selectDepartureDateTime(page);
  await page.locator("button:nth-child(6)").first().click();
  await selectOneWayTripOffer(page);
}

export async function bookRoundTrip(page: Page): Promise<void> {
  console.log(`[*] Entering origin and destination for one-way trip...`);
  await page.waitForURL("**/trip-management/book/rail");
  await checkIfRoundTripEnabled(page);
  await selectRoundTripOption(page);
  await enterOriginDestination(page);

  await selectOutboundTripDateTime(page);
  await selectInboundTripDateTime(page);
  await page.locator("button:nth-child(7)").first().click();

  await selectRoundTripOffer(page);
  await page.pause();
}
export async function selectOutboundTripDateTime(page: Page): Promise<void> {
  console.log("[*] Selecting outbound trip date and time...");
  await page.getByRole("group", { name: "Outbound *" }).getByLabel("Open date picker").click();
  await page.getByLabel("Wednesday, 27 March").click();
  await page.getByRole("button", { name: "23:" }).click();
}

export async function selectInboundTripDateTime(page: Page): Promise<void> {
  console.log("[*] Selecting inbound date and time...");
  await page.getByRole("group", { name: "Inbound *" }).getByLabel("Open date picker").click();
  await page.getByLabel("Friday, 29 March").click();
  await page.getByRole("button", { name: "23:" }).click();
}
export async function selectDepartureDateTime(page: Page): Promise<void> {
  await page.getByLabel("Open date picker").click();
  await page.getByLabel("Friday, 29 March").click();
  await page.getByRole("button", { name: "23:" }).click();
}

export async function checkIfRoundTripEnabled(page: Page): Promise<void> {
  console.log(`[*] Refreshing page to work around feature flag bug...`);
  await page.goto("http://localhost:5173/trip-management/book/rail");

  console.log("[*] Checking if round trip feature is enabled...");
  const roundTripButton = page.getByText("Round trip");
  if (!roundTripButton) {
    console.error(
      "ERROR: Round trip feature is not enabled for the current user. Enable round trip feature for current user in the 'feature-flags.ts' file.",
    );
    throw new Error("Round trip feature is not enabled for the current user");
  }
}

export async function selectOneWayTripOption(page: Page): Promise<void> {
  console.log("[*] Selecting one-way trip option...");

  // TODO(2024-03-20/alvin.s): This will only be available if the `Feature.CAR_RENTAL` flag is enabled. Use `getAvailableFeatures`.
  // await page.getByRole("link", { name: "Train" }).click();
  // await page.getByTestId("rail").click();

  // Define the locator for the 'One way' option
  const oneWayOption = page.getByTestId("one-way");
  console.log(oneWayOption);

  // Wait for the 'One way' option to be visible and enabled
  await oneWayOption.waitFor({ state: "visible" });
  // Wait until the element is visible
  await oneWayOption.check();

  // Check if the one-way option is already checked
  if (!(await oneWayOption.isChecked())) {
    // If not, try to check it
    await oneWayOption.check();

    // Wait for the radio button to become checked to confirm the action was successful
    await oneWayOption.isChecked({ timeout: 3000 });
    // Adjust the timeout as needed
  }

  console.log("[*] 'One way' trip option selected.");
}

export async function selectRoundTripOption(page: Page): Promise<void> {
  console.log("[*] Selecting Round Trip option...");
  await page.getByRole("link", { name: "Train" }).click();
  // Define the locator for the 'One way' option
  const roundTripOption = page.getByLabel("Round trip");

  // Wait for the 'One way' option to be visible and enabled
  await roundTripOption.waitFor({ state: "visible" });
  // Wait until the element is visible
  await roundTripOption.check();

  // Check if the one-way option is already checked
  if (!(await roundTripOption.isChecked())) {
    // If not, try to check it
    await roundTripOption.check();

    // Wait for the radio button to become checked to confirm the action was successful
    // Adjust the timeout as needed
    await roundTripOption.isChecked({ timeout: 3000 });
  }

  console.log("[*] 'One way' trip option selected.");
}

export async function enterOriginDestination(page: Page): Promise<void> {
  await page.getByLabel("From *").click();
  await page.getByLabel("From *").fill("Salzburg Hauptbahnhof");
  await page.getByText("Salzburg Hauptbahnhof (S-Bahn").click();
  await page.getByLabel("To *").click();
  await page.getByLabel("To *").fill("Munich Central Station");
  await page.getByText("Munich Central Station,").click();
}

export async function selectOutboundTripOffer(page: Page): Promise<void> {
  await page.pause();
  await page.getByRole("main").locator("div").filter({ hasText: "Time remaining" }).nth(2).click();
  await page.locator("li").filter({ hasText: "stop" }).getByRole("button").click();
  await page.getByRole("button", { name: "Confirm selection" }).click();
}

export async function selectInboundTripOffer(page: Page): Promise<void> {
  await page.pause();
  await page.locator("li").filter({ hasText: "stop" }).getByRole("button").click();

  await page.getByRole("button", { name: "Book now" }).click();
  await page.getByRole("button", { name: "Next" }).click();
}

export async function clickSearchButton(page: Page): Promise<void> {
  console.log("[*] Clicking the search button to request offers...");
  await page.locator("button:nth-child(7)").click();
}

export async function checkOffers(page: Page): Promise<boolean> {
  console.log("[*] Checking if offers for trip were found...");
  // Check if any list item contains 'No trips found'
  const noTripsFound = await page.locator('li >> text="No trips found"').count();

  // If 'No trips found' is present (count > 0), then no offers are available
  if (noTripsFound > 0) {
    console.log("No trip offers were found.");
    // Return false indicating no offers found
    return false;
  }
  // If 'No trips found' is not present, then offers are available
  console.log("Trip offers are available.");
  return true;
}

export async function selectOneWayTripOffer(page: Page): Promise<void> {
  console.log(`[*] Selecting ao offer for a one-way trip...`);
  const offersAvailable = await checkOffers(page);
  if (offersAvailable) {
    // Proceed with the test assuming offers are available
    console.log("[*] Offers were found...");
  } else {
    // Handle the case where no offers are found, possibly by skipping further steps or failing the test
    console.log("[*] Offers were not found...");
    throw new Error("No trip offers were found, ending test.");
  }
  // This finds the first list item (`li`) that contains the text 'stop' within it.
  // It then finds a button within that list item and clicks it.
  // The use of `first()` ensures that it targets the first matching element.
  const offerLocator = page.locator("li").filter({ hasText: "stop" }).locator("button").first();

  // Wait for the offer locator to be visible before attempting to click on it.
  // This helps avoid issues where the script tries to interact with elements that are not yet ready.
  await offerLocator.waitFor({ state: "visible" });

  // Click the offer. This assumes there is a button within the list item that needs to be clicked.
  await offerLocator.click();
  console.log(`[*] Clicking the 'Book Now' button...`);
  await page.getByRole("button", { name: "Book now" }).click();
}

export async function selectRoundTripOffer(page: Page): Promise<void> {
  console.log(`[*] Selecting a round trip offer...`);
  const offersAvailable = await checkOffers(page);
  if (offersAvailable) {
    // Proceed with the test assuming offers are available
    console.log("[*] Offers were found...");
  } else {
    // Handle the case where no offers are found, possibly by skipping further steps or failing the test
    console.log("[*] Offers were not found...");
    throw new Error("No trip offers were found, ending test.");
  }
  // This finds the first list item (`li`) that contains the text 'stop' within it.
  // It then finds a button within that list item and clicks it.
  // The use of `first()` ensures that it targets the first matching element.
  const offerLocator = page.locator("li").filter({ hasText: "stop" }).locator("button").first();

  // Wait for the offer locator to be visible before attempting to click on it.
  // This helps avoid issues where the script tries to interact with elements that are not yet ready.
  await offerLocator.waitFor({ state: "visible" });

  // Click the offer. This assumes there is a button within the list item that needs to be clicked.
  await offerLocator.click();
  console.log(`[*] Clicking the 'Book Now' button...`);
  await page.getByRole("button", { name: "Book now" }).click();
}
