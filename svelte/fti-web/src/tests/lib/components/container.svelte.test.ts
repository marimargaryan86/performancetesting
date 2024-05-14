import "@testing-library/jest-dom/vitest";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/svelte";
import Container from "$lib/components/container.svelte";

describe("Container Component", () => {
  it("should render a title", () => {
    render(Container, { title: "Hello World" });

    const titleString = screen.getByText("Hello World");
    expect(titleString).toBeVisible();
  });
});
