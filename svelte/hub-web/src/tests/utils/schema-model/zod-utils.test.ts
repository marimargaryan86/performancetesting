import { zodNonNullish, zodNonOptional } from "utils/schema-model/zod-utils";
import { describe, expect, it } from "vitest";
import { z } from "zod";

describe("zodNonNullish", () => {
  it("Should create a non-nullish Zod schema", () => {
    const schema = z.string().optional().nullable();
    const schema2 = z.string().optional().nullable().optional().nullable();

    const parsed = zodNonNullish(schema);
    const parsed2 = zodNonNullish(schema2);

    expect(schema.isOptional()).toBeTruthy();
    expect(parsed.isOptional()).toBeFalsy();
    expect(schema.isNullable()).toBeTruthy();
    expect(parsed.isNullable()).toBeFalsy();

    expect(schema2.isOptional()).toBeTruthy();
    expect(parsed2.isOptional()).toBeFalsy();
    expect(schema2.isNullable()).toBeTruthy();
    expect(parsed2.isNullable()).toBeFalsy();
  });
});

describe("zodNonOptional", () => {
  it("Should create a non optional Zod schema", () => {
    const schema = z.string().optional().nullable();
    const schema2 = z.string().optional().nullable().optional().nullable();

    const parsed = zodNonOptional(schema);
    const parsed2 = zodNonOptional(schema2);

    expect(schema.isOptional()).toBeTruthy();
    expect(parsed.isOptional()).toBeFalsy();
    expect(schema.isNullable()).toBeTruthy();
    expect(parsed.isNullable()).toBeTruthy();

    expect(schema2.isOptional()).toBeTruthy();
    expect(parsed2.isOptional()).toBeFalsy();
    expect(schema2.isNullable()).toBeTruthy();
    expect(parsed2.isNullable()).toBeTruthy();
  });
});
