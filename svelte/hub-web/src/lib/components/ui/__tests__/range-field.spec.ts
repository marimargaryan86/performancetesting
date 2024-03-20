import "@testing-library/jest-dom/vitest";
import { render, fireEvent } from "@testing-library/svelte";
import { vi, describe, expect, it, beforeEach, afterEach } from "vitest";
import RangeField from "../range-field.svelte";

describe("range field ui", () => {
  let originalGetBoundingClientRect: typeof Element.prototype.getBoundingClientRect;

  beforeEach(() => {
    // We need to mock getBoundingClientRect since it would otherwise always return 0
    originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
    Element.prototype.getBoundingClientRect = vi.fn(() => ({
      width: 100,
      height: 40,
      top: 0,
      left: 0,
      bottom: 0,
      right: 0,
      x: 0,
      y: 0,
      toJSON: () => {},
    }));
  });

  afterEach(() => {
    // Restore the original getBoundingClientRect after each test
    Element.prototype.getBoundingClientRect = originalGetBoundingClientRect;
  });

  it("should render with initial single value", () => {
    const { container, component, getAllByRole } = render(RangeField, {
      min: 0,
      max: 100,
      value: 50,
    });
    expect(container).toBeInTheDocument();
    const [handle, nonExistentHandle] = getAllByRole("slider");
    expect(handle).toBeInTheDocument();
    expect(nonExistentHandle).toBeUndefined();
    expect(component.value).toEqual(50);
    const ariaValueNow = handle?.getAttribute("aria-valuenow");
    expect(ariaValueNow).toEqual("50");
  });

  it("should render with initial range value", () => {
    const { container, component, getAllByRole } = render(RangeField, {
      min: 0,
      max: 100,
      value: { start: 25, end: 75 },
    });
    expect(container).toBeInTheDocument();
    const [startHandle, endHandle] = getAllByRole("slider");
    expect(component.value).toEqual({ start: 25, end: 75 });
    const startAriaValueNow = startHandle?.getAttribute("aria-valuenow");
    expect(startAriaValueNow).toEqual("25");
    const endAriaValueNow = endHandle?.getAttribute("aria-valuenow");
    expect(endAriaValueNow).toEqual("75");
  });

  it("should update single value on mouse drag", async () => {
    const { getAllByRole } = render(RangeField, { min: 0, max: 100, value: 50 });
    const [handle] = getAllByRole("slider");

    await fireEvent(handle as HTMLElement, new MouseEvent("dragstart"));
    await fireEvent(
      handle as HTMLElement,
      new MouseEvent("mousemove", { bubbles: true, clientX: 3 }),
    );
    await fireEvent(
      handle as HTMLElement,
      new MouseEvent("mouseup", { bubbles: true, clientX: 3 }),
    );

    const ariaValueNow = handle?.getAttribute("aria-valuenow");
    expect(ariaValueNow).toEqual("53");
  });

  it("should not allow the start value to exceed the end value", async () => {
    const { getAllByRole } = render(RangeField, {
      min: 0,
      max: 100,
      value: { start: 20, end: 50 },
    });
    const [handle] = getAllByRole("slider");

    await fireEvent(handle as HTMLElement, new MouseEvent("dragstart"));
    await fireEvent(
      handle as HTMLElement,
      new MouseEvent("mousemove", { bubbles: true, clientX: 100 }),
    );
    await fireEvent(
      handle as HTMLElement,
      new MouseEvent("mouseup", { bubbles: true, clientX: 100 }),
    );

    const ariaValueNow = handle?.getAttribute("aria-valuenow");
    expect(ariaValueNow).toEqual("50");
  });
});
