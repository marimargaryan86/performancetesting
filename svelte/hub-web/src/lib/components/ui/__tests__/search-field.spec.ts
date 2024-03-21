import "@testing-library/jest-dom/vitest";
import { render } from "@testing-library/svelte";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import SearchField from "./search-field-wrapper.svelte";
import { get, writable } from "svelte/store";

describe("search field ui", () => {
  it("should render successfully", () => {
    const { getByRole } = render(SearchField);
    const searchField = getByRole("searchbox");
    expect(searchField).toBeInTheDocument();
  });

  it("should update value on input", async () => {
    const value = writable("");
    const clearValue = writable("");
    const { getByRole } = render(SearchField, { value, clearValue });
    const searchField = getByRole("searchbox") as HTMLInputElement;
    const user = userEvent.setup();
    await user.type(searchField, "test");
    expect(searchField.value).toEqual("test");
    expect(get(value)).toEqual("test");
  });

  it("should clear value when clear button is clicked", async () => {
    const value = writable("test");
    const clearValue = writable("");
    const { getByRole } = render(SearchField, { clearable: true, value, clearValue });
    const searchField = getByRole("searchbox") as HTMLInputElement;
    const clearButton = getByRole("button") as HTMLButtonElement;
    expect(clearButton).toBeInTheDocument();
    const user = userEvent.setup();
    await user.click(clearButton);
    expect(searchField.value).toBe("");
  });
});
