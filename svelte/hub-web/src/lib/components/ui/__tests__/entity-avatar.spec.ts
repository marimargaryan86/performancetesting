import "@testing-library/jest-dom/vitest";
import { describe, expect, it } from "vitest";
import { render } from "@testing-library/svelte";
import EntityAvatar from "../entity-avatar.svelte";

describe("entity avatar ui", () => {
  it("should render successfully", () => {
    const { getByRole } = render(EntityAvatar);
    const avatar = getByRole("presentation");
    expect(avatar).toBeInTheDocument();
  });

  it("should display image when imageUrl is provided", () => {
    const { getByRole } = render(EntityAvatar, { imageUrl: "its-fine.gif" });
    const avatar = getByRole("presentation") as HTMLImageElement;
    expect(avatar).toBeInTheDocument();
    expect(avatar.src).toBe("its-fine.gif");
  });

  it("should display initials when name is provided and imageUrl is not", () => {
    const { getByText } = render(EntityAvatar, { name: "Tester Testerson" });
    const initials = getByText("TT");
    expect(initials).toBeInTheDocument();
  });

  it("should display `?` when neither name nor imageUrl is provided", () => {
    const { getByText } = render(EntityAvatar);
    const placeholder = getByText("?");
    expect(placeholder).toBeInTheDocument();
  });
});
