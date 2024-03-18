import "@testing-library/jest-dom/vitest";
import { describe, expect, it } from "vitest";
import { render } from "@testing-library/svelte";
import Card from "../card.svelte";

describe("card ui component", () => {
  // The card component is extremely simple and we consider it an anti-pattern to test slots
  // so this test is more of a placeholder if we decide to add additional logic to the
  // component at a later stage
  it("should render the card with the given variant and theme", () => {
    const { getByRole } = render(Card, { props: { variant: "vertical", theme: "dark" } });
    const card = getByRole("presentation");
    expect(card).toHaveClass("card", "vertical", "dark");
  });
});
