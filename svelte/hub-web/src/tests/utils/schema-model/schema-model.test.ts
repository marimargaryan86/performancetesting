import { identifier, links, relationships, create } from "utils/schema-model/schema-model";
import { describe, expect, it } from "vitest";
import { z } from "zod";

describe("identifier", () => {
  it("Should create a schema identifier", () => {
    const schema = z.object({ id: z.string(), type: z.enum(["test"]), prop: z.number() });
    const ident = identifier(schema);

    expect(Object.keys(ident.shape)).length(2);
    expect(Object.keys(ident.shape)).contain("id");
    expect(Object.keys(ident.shape)).contain("type");
    expect(ident.shape.id).toBe(schema.shape.id);
    expect(ident.shape.type).toBe(schema.shape.type);
  });
});

describe("links", () => {
  it("Should create a schema self link", () => {
    const lnks = links({ self: true });

    expect(Object.keys(lnks.shape)).length(1);
    expect(Object.keys(lnks.shape)).contain("self");
    expect(lnks.shape.self).instanceOf(z.ZodString);
  });

  it("Should create a schema next link", () => {
    const lnks = links({ next: true });

    expect(Object.keys(lnks.shape)).length(1);
    expect(Object.keys(lnks.shape)).contain("next");
    expect(lnks.shape.next).instanceOf(z.ZodString);
  });

  it("Should create schema next- and self links", () => {
    const lnks = links({ next: true, self: true });

    expect(Object.keys(lnks.shape)).length(2);
    expect(Object.keys(lnks.shape)).contain("next");
    expect(Object.keys(lnks.shape)).contain("self");
    expect(lnks.shape.next).instanceOf(z.ZodString);
    expect(lnks.shape.self).instanceOf(z.ZodString);
  });
});

describe("relationships", () => {
  it("Should create a relationships schema", () => {
    const rel = relationships({
      test: z.array(z.string()),
      opt: z.object({ name: z.string() }).optional(),
      nil: z.object({ age: z.number() }).nullable(),
      optNil: z.number().optional().nullable(),
    });

    expect(rel.shape.test.shape.data).instanceOf(z.ZodArray);
    expect(rel.shape.opt).instanceOf(z.ZodOptional);
    expect(rel.shape.opt.unwrap().shape.data).instanceOf(z.ZodObject);
    expect(rel.shape.nil.shape.data).instanceOf(z.ZodNullable);
    expect(rel.shape.nil.shape.data.unwrap()).instanceOf(z.ZodObject);
    expect(rel.shape.optNil).instanceOf(z.ZodOptional);
    expect(rel.shape.optNil.unwrap().shape.data).instanceOf(z.ZodNullable);
    expect(rel.shape.optNil.unwrap().shape.data.unwrap()).instanceOf(z.ZodNumber);
  });
});

const sm = create({
  schema: z.object({
    id: z.string(),
    type: z.enum(["test"]),
    attributes: z.object({
      name: z.string(),
      dob: z.date().nullable(),
    }),
  }),
  model: z.object({
    id: z.string(),
    name: z.string(),
    dob: z.date().optional(),
  }),
  toModel: (data) => ({
    id: data.id,
    name: data.attributes.name,
    dob: data.attributes.dob ?? undefined,
  }),
  toSchema: (data) =>
    ({
      id: data.id,
      type: "test",
      attributes: {
        name: data.name,
        dob: data.dob ?? null,
      },
    } as const),
});

describe("create", () => {
  it("Should create a schema model", () => {
    expect(Object.keys(sm.identifier.shape)).length(2);
    expect(Object.keys(sm.identifier.shape)).contain("id");
    expect(Object.keys(sm.identifier.shape)).contain("type");

    expect(Object.keys(sm.schema.shape)).length(3);
    expect(Object.keys(sm.schema.shape)).contain("id");
    expect(Object.keys(sm.schema.shape)).contain("type");
    expect(Object.keys(sm.schema.shape)).contain("attributes");
    expect(Object.keys(sm.schema.shape.attributes.shape)).length(2);
    expect(Object.keys(sm.schema.shape.attributes.shape)).contain("name");
    expect(Object.keys(sm.schema.shape.attributes.shape)).contain("dob");

    expect(Object.keys(sm.model.shape)).length(3);
    expect(Object.keys(sm.model.shape)).contain("id");
    expect(Object.keys(sm.model.shape)).contain("name");
    expect(Object.keys(sm.model.shape)).contain("dob");

    expect(
      sm.toModel({ id: "i", type: "test", attributes: { name: "n", dob: new Date() } }),
    ).toBeTruthy();
    expect(() => sm.toModel({ id: "i", type: "test", attributes: { dob: null } })).toThrow(
      z.ZodError,
    );
    expect(sm.toSchema({ id: "i", name: "n", dob: new Date() })).toBeTruthy();
    expect(() => sm.toSchema({ id: "i", dob: new Date() })).toThrow(z.ZodError);
  });
});
