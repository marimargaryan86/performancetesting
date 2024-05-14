import "@testing-library/jest-dom/vitest";
import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/svelte";
import IconList, {
  type IconListConfig,
  type IconListItemConfig,
} from "$lib/components/icon-list.svelte";
import { toAriaLabel } from "$lib/components/icon.svelte";

const MOCK_ICON_LIST: IconListConfig = [
  { iconType: "wifi", label: "foo" },
  { iconType: "pool", label: "bar" },
  { iconType: "parking", label: "baz" },
  { iconType: "bar", label: "quux" },
  { iconType: "gym", label: "test" },
];

describe("IconList Component", () => {
  beforeEach(() => {
    render(IconList, { iconList: MOCK_ICON_LIST });
  });

  it.each(MOCK_ICON_LIST)(
    "should render a list of labeled icons",
    ({ iconType, label }: IconListItemConfig) => {
      const listItem = screen.getByText(label);

      expect(listItem.textContent?.trimStart()).toEqual(label);

      const ariaLabel = toAriaLabel(iconType);
      const icon = screen.getByRole("img", { name: ariaLabel });
      const iconStyles = icon.getAttribute("style");

      expect(iconStyles).toContain(iconType);
    },
  );
});

describe("IconList Component with formatter", () => {
  const firstIcon = MOCK_ICON_LIST[0];
  const formatter = (label: string) => label.toUpperCase();

  beforeEach(() => {
    render(IconList, { iconList: [firstIcon], formatter });
  });

  it("should format the label string correctly", () => {
    const query = formatter(firstIcon.label);
    const listItem = screen.getByText(query);

    expect(listItem).toBeVisible();
  });
});

/** TODO(2024-05-14/a.santos): figure out of it's worth testing CSS. */
describe.skip("IconList Component with variants", () => {
  beforeEach(() => {
    render(IconList, { iconList: MOCK_ICON_LIST, variant: "column" });
  });

  it.skip("should render columns or rows as specified.");
});
