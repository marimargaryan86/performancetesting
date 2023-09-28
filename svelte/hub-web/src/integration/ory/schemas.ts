import { getSchemaModel, type Infer } from "integration/common/schema-model.server";
import { z } from "zod";

export const loginFormModel = getSchemaModel(
  z.object({
    id: z.string(),
    ui: z.object({
      nodes: z.array(
        z.object({
          attributes: z.object({
            // eslint-disable-next-line camelcase
            node_type: z.enum(["text", "a", "img", "input", "script"]),
            type: z.enum([
              "text",
              "password",
              "number",
              "checkbox",
              "hidden",
              "email",
              "tel",
              "submit",
              "button",
              "datetime-local",
              "date",
              "url",
            ]),
            name: z.string(),
            value: z.string().optional(),
          }),
          meta: z.object({
            label: z.object({ text: z.string() }).optional(),
          }),
        }),
      ),
    }),
  }),
  z.object({
    id: z.string(),
    elements: z.array(
      z.object({
        type: z.enum(["text", "a", "img", "input", "script"]),
        attributes: z.object({
          label: z.string().optional(),
          name: z.string(),
          value: z.string(),
          type: z.enum([
            "text",
            "password",
            "number",
            "checkbox",
            "hidden",
            "email",
            "tel",
            "submit",
            "button",
            "datetime-local",
            "date",
            "url",
          ]),
        }),
      }),
    ),
  }),
  {
    toModel: (data) => ({
      id: data.id,
      elements: data.ui.nodes.map((item) => ({
        type: item.attributes.node_type,
        attributes: {
          name: item.attributes.name,
          type: item.attributes.type,
          value: item.attributes.value ?? "",
          label: item.meta.label?.text,
        },
      })),
    }),
  },
);
export type LoginFormModel = Infer<typeof loginFormModel>;

export const sessionModel = getSchemaModel(
  z.object({
    // eslint-disable-next-line camelcase
    expires_at: z.date({ coerce: true }),
    identity: z.object({
      id: z.string(),
      traits: z.object({
        email: z.string().email(),
      }),
    }),
  }),
  z.object({
    data: z.object({
      id: z.string(),
      email: z.string().email(),
      name: z.string(),
    }),
    expiresAt: z.date(),
  }),
  {
    toModel: (data) => ({
      data: {
        id: data.identity.id,
        email: data.identity.traits.email,
        name: "Unknown",
      },
      expiresAt: data.expires_at,
    }),
  },
);
export type OrySessionModel = Infer<typeof sessionModel>;
