import "@testing-library/jest-dom/vitest";
import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@testing-library/svelte";
import userEvent from "@testing-library/user-event";
import Backdrop from "../backdrop.svelte";

describe("backdrop ui component", () => {
  it("should show backdrop when open function is called", async () => {
    const { component } = render(Backdrop);
    component.open();
    await waitFor(() => {
      expect(screen.queryByRole("presentation")).toBeInTheDocument();
    });
  });

  it("should hide backdrop when close function is called", async () => {
    const { component } = render(Backdrop);
    component.open();
    await waitFor(() => {
      expect(screen.queryByRole("presentation")).toBeInTheDocument();
    });
    component.close();
    await waitFor(() => {
      expect(screen.queryByRole("presentation")).not.toBeInTheDocument();
    });
  });

  it("should toggle backdrop when toggle function is called", async () => {
    const { component } = render(Backdrop);
    component.toggle();
    await waitFor(() => {
      expect(screen.queryByRole("presentation")).toBeInTheDocument();
    });
    component.toggle();
    await waitFor(() => {
      expect(screen.queryByRole("presentation")).not.toBeInTheDocument();
    });
  });

  it("should hide backdrop when it is clicked on", async () => {
    const { component } = render(Backdrop);
    component.open();
    await waitFor(() => {
      expect(screen.queryByRole("presentation")).toBeInTheDocument();
    });
    const user = userEvent.setup();
    await user.click(screen.getByRole("presentation"));
    await waitFor(() => {
      expect(screen.queryByRole("presentation")).not.toBeInTheDocument();
    });
  });
});
