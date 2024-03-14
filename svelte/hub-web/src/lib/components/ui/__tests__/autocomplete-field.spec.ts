import "@testing-library/jest-dom/vitest";
import { describe, expect, it } from "vitest";
import userEvent from "@testing-library/user-event";
import { render, screen, waitFor } from "@testing-library/svelte";
import AutocompleteField from "./autocomplete-field-wrapper.svelte";
import { get, writable } from "svelte/store";

describe("autocomplete-field ui component", () => {
  it("should render the autocomplete field with the given label", () => {
    render(AutocompleteField, {
      props: { label: "Test", value: writable(undefined) },
    });
    expect(screen.getByLabelText("Test")).toBeInTheDocument();
  });

  it("should render the options when input is given", async () => {
    render(AutocompleteField, {
      props: {
        autocomplete: () => ["Option 1", "Option 2"],
        value: writable(undefined),
      },
    });
    const user = userEvent.setup();
    const input = screen.getByRole<HTMLInputElement>("list");
    await user.type(input, "Option");
    expect(screen.getByText("Option 1")).toBeInTheDocument();
    expect(screen.getByText("Option 2")).toBeInTheDocument();
  });

  it("should render the options using formatter when input is given", async () => {
    const data = [
      { id: "opt1", label: "Option 1" },
      { id: "opt2", label: "Option 2" },
    ];
    type DataType = (typeof data)[number];
    render(AutocompleteField<DataType>, {
      props: {
        value: writable(undefined),
        autocomplete: () => data,
        formatter: (sel) => sel?.label || "",
      },
    });
    const user = userEvent.setup();
    const input = screen.getByRole<HTMLInputElement>("list");
    await user.type(input, "Option");
    expect(screen.getByText("Option 1")).toBeInTheDocument();
    expect(screen.getByText("Option 2")).toBeInTheDocument();
  });

  it("should select an option when it is clicked", async () => {
    const items = [
      { id: "opt1", label: "Option 1" },
      { id: "opt2", label: "Option 2" },
    ];
    type DataType = (typeof items)[number];
    const { component } = render(AutocompleteField<DataType>, {
      props: {
        value: writable(undefined),
        autocomplete: () => items,
        formatter: (sel) => sel?.label || "",
      },
    });
    const user = userEvent.setup();
    const input = screen.getByRole<HTMLInputElement>("list");
    await user.type(input, "Option");
    const options = screen.getAllByRole("option");
    expect(options.length).toBeGreaterThan(0);
    expect(options[0]).toBeInTheDocument();
    expect(options[1]).toBeInTheDocument();
    expect(get(component.value)).toBe(undefined);
    expect(options[1]).not.toHaveClass("selected", "hovered");
    await user.click(options[1] as HTMLElement);
    await waitFor(() => {
      expect(screen.queryAllByRole("option")).toEqual([]);
      expect(get(component.value)).toBe(items[1]);
    });
  });

  it("should emulate mouse actions when using keyboard", async () => {
    const items = [
      { id: "opt1", label: "Option 1" },
      { id: "opt2", label: "Option 2" },
      { id: "opt3", label: "Option 3" },
    ];
    type DataType = (typeof items)[number];
    const { component } = render(AutocompleteField<DataType>, {
      props: {
        value: writable(undefined),
        autocomplete: () => items,
        formatter: (sel) => sel?.label || "",
      },
    });
    const user = userEvent.setup();
    const input = screen.getByRole<HTMLInputElement>("list");
    await user.type(input, "Option");
    const options = screen.getAllByRole("option");

    expect(options.length).toBeGreaterThan(0);
    expect(options[0]).toBeInTheDocument();
    expect(options[0]).not.toHaveClass("hovered");

    await user.keyboard("{arrowdown}");
    expect(options[0]).toHaveClass("hovered");

    await user.keyboard("{arrowdown}");
    expect(options[0]).not.toHaveClass("hovered");
    expect(options[1]).toHaveClass("hovered");

    await user.keyboard("{arrowdown}");
    expect(options[1]).not.toHaveClass("hovered");
    expect(options[2]).toHaveClass("hovered");

    await user.keyboard("{arrowup}");
    expect(options[2]).not.toHaveClass("hovered");
    expect(options[1]).toHaveClass("hovered");

    await user.keyboard("{enter}");
    expect(get(component.value)).toBe(items[1]);
  });
});
