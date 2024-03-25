import { describe, expect, it } from "vitest";
import "@testing-library/jest-dom/vitest";
import { render, screen, fireEvent, waitForElementToBeRemoved } from "@testing-library/svelte";
import Alert from "../alert.svelte";

describe("alert ui component", () => {
  it("should render a success alert", () => {
    render(Alert, { props: { type: "success" } });
    const alert = screen.getByRole("alert");
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveClass("success");
  });

  it("should render a warning alert", () => {
    render(Alert, { props: { type: "warning" } });
    const alert = screen.getByRole("alert");
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveClass("warning");
  });

  it("should render an error alert", () => {
    render(Alert, { props: { type: "error" } });
    const alert = screen.getByRole("alert");
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveClass("error");
  });

  it("should hide the alert when the close button is clicked", async () => {
    render(Alert, { props: { type: "success", dismissable: true } });
    const alert = screen.getByRole("alert");
    expect(alert).toBeInTheDocument();
    const closeButton = screen.getByRole("button");
    expect(closeButton).toBeInTheDocument();
    await fireEvent.click(closeButton);
    await waitForElementToBeRemoved(alert);
    expect(alert).not.toBeInTheDocument();
  });

  it("should render the close button when dismissable is true", () => {
    render(Alert, { props: { dismissable: true } });
    expect(screen.queryByRole("button")).toBeInTheDocument();
  });

  it("should not render the close button when dismissable is false", () => {
    render(Alert, { props: { dismissable: false } });
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
