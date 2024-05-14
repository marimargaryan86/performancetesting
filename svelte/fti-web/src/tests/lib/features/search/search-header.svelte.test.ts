import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen } from "@testing-library/svelte";
import SearchHeader from "$lib/features/search/search-header.svelte";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import type { SearchOptions } from "$lib/models/common";

describe("SearchHeader with default options", () => {
  beforeEach(() => {
    render(SearchHeader);
    window.location.pathname = "/search/test";
  });

  afterEach(() => {
    cleanup();
  });

  it("has an icon link that navigates back to home", async () => {
    const iconLink = await screen.getByRole("link", { name: "BigXtra logo" });

    expect(iconLink).toBeVisible();
    expect(window.location.pathname).toEqual("/search/test");
    iconLink?.click();
    expect(window.location.pathname).toEqual("/");
  });

  // TODO(04-26-2024/a.santos): Get real support number.
  it("has like icons and the correct phone number link", () => {
    const likeLink = screen.getByRole("link", { description: "search-header-heart-icon" });
    const likeIcon = likeLink.children[0];
    expect(likeIcon).toBeVisible();

    const likeIconStyles = likeIcon.getAttribute("style");
    expect(likeIconStyles).toContain('url("/icons/heart-');

    const phoneLink = screen.getByTestId("phoneLink");
    expect(phoneLink).toBeVisible();

    const telephoneNumber = phoneLink.getAttribute("href");
    expect(telephoneNumber).toContain("tel:");
  });
});

describe("SearchHeader with passed-in search options", () => {
  const customSearchOptions: SearchOptions = {
    origin: "munich",
    destination: "bali",
    searchType: "hotels",
    passengers: { adults: 2, children: 1 },
    rooms: [
      { adults: 1, children: 1 },
      { adults: 1, children: 0 },
    ],
    dates: {
      start: "12/20/2024",
      end: "01/07/2025",
    },
  };

  it("should render the correct values for the search options", () => {
    render(SearchHeader, { searchOptions: customSearchOptions });
    window.location.pathname = "/search/test";

    const originAndDestination = screen.getByLabelText("Origin-Destination");
    expect(originAndDestination).toBeVisible();
    expect(originAndDestination).toHaveValue("Munich-Bali");

    const dates = screen.getByLabelText("Dates");
    expect(dates).toBeVisible();
    expect(dates).toHaveValue("12/20/2024-01/07/2025");

    const passengersAndRooms = screen.getByLabelText("Passengers and Rooms");
    expect(passengersAndRooms).toBeVisible();
    expect(passengersAndRooms).toHaveValue("2 adults, 1 child, 2 rooms");

    cleanup();
  });
});
