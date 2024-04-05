import { describe, expect, it } from "vitest";
import { stringifySchema } from "../schema";

describe("stringifySchema", () => {
  it("Should stringify a schema", () => {
    expect(stringifySchema({ read: "foo", write: "bar" }, "read")).toBe("foo");
    expect(stringifySchema({ read: "foo", write: "bar" }, "write")).toBe("bar");
    expect(stringifySchema({ read: "foo", write: undefined }, "write")).toBe("undefined");
  });
});
