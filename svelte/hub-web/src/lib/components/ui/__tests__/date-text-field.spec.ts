import { render, waitFor } from "@testing-library/svelte";
import { describe, expect, it } from "vitest";
import userEvent from "@testing-library/user-event";
import DateTextField from "./date-text-field-wrapper.svelte";
import { get, writable } from "svelte/store";

describe("DateTextField", () => {
  const initialDate = new Date("2022-01-01T00:00:00.000");

  it("should render successfully", () => {
    const { getByRole } = render(DateTextField, {
      value: writable(initialDate),
    });
    const textField = getByRole("textbox");
    expect(textField).toBeInTheDocument();
  });

  it("should display placeholder", () => {
    const { getByPlaceholderText } = render(DateTextField, {
      placeholder: "MM/DD/YYYY",
      value: writable(initialDate),
    });
    const textField = getByPlaceholderText("MM/DD/YYYY");
    expect(textField).toBeInTheDocument();
  });

  it("should update value on input", async () => {
    const { component, getByRole } = render(DateTextField, {
      props: {
        value: writable(initialDate),
      },
    });
    const textField = getByRole("textbox");
    const user = userEvent.setup();
    await user.clear(textField);
    await user.type(textField, "01/01/2022");
    await waitFor(() => {
      const value = get(component.value) as Date;
      expect(value.toISOString()).toBe(initialDate.toISOString());
    });
  });

  it("should validate and show error for invalid date", async () => {
    const { getByPlaceholderText, findByText } = render(DateTextField, {
      props: {
        value: writable(initialDate),
      },
    });
    const textField = getByPlaceholderText("DD/MM/YYYY");
    const user = userEvent.setup();
    await user.clear(textField);
    await user.type(textField, "99/99/9999");
    await waitFor(async () => {
      const error = await findByText("Invalid day., Invalid month.");
      expect(error).toBeInTheDocument();
    });
  });
});
