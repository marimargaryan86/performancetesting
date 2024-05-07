import { describe, expect, it } from "vitest";
import { toTitleCase } from "$lib/helpers/common";

describe("toTitleCase", () => {
  it("converts a lowercase sentence to title case", () => {
    expect(toTitleCase("hello world from typescript")).toBe("Hello World From Typescript");
  });

  it("properly handles a string that is already in title case", () => {
    expect(toTitleCase("Hello World From Typescript")).toBe("Hello World From Typescript");
  });

  it("converts an all uppercase sentence to title case", () => {
    expect(toTitleCase("HELLO WORLD FROM TYPESCRIPT")).toBe("Hello World From Typescript");
  });

  it("handles mixed case input", () => {
    expect(toTitleCase("HeLLo WoRLd fROm TyPeScRipT")).toBe("Hello World From Typescript");
  });

  it("returns an empty string if provided an empty string", () => {
    expect(toTitleCase("")).toBe("");
  });

  it("handles strings with punctuation correctly", () => {
    expect(toTitleCase("hello, world! how are you?")).toBe("Hello, World! How Are You?");
  });

  it("handles strings with numbers and special characters", () => {
    expect(toTitleCase("1234 hello #world")).toBe("1234 Hello #world");
  });
});
