import { describe, it, expect } from "vitest";
import { conditionalQuotes, toStringObject } from "../helpers";

describe("conditionalQuotes", () => {
  it("Should wrap invalid javascript variable names in quotes", () => {
    expect(conditionalQuotes("foo")).toBe("foo");
    expect(conditionalQuotes("Foo")).toBe("Foo");
    expect(conditionalQuotes("f1oo")).toBe("f1oo");
    expect(conditionalQuotes("$foo")).toBe("$foo");
    expect(conditionalQuotes("1Foo")).toBe('"1Foo"');
    expect(conditionalQuotes("Foo[bar]")).toBe('"Foo[bar]"');
  });
});

describe("toStringObject", () => {
  it("Should stringify an object", () => {
    expect(toStringObject(['foo: "bar"'], 0)).toBe(`\
{
  foo: "bar";
}`);
  });
  expect(toStringObject(['foo: "bar"', 'bar: "baz"'], 0)).toBe(`\
{
  foo: "bar";
  bar: "baz";
}`);
});
