import { z } from "zod";
import { companyModel } from "./company";
import schemaModel, { type Infer } from "utils/schema-model";

export const contactModel = z.object({ id: z.string(), type: z.literal("contacts") });

export const accountModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.literal("accounts"),
    attributes: z.object({
      name: z.string(),
      status: z.string(),
    }),
    relationships: schemaModel.relationships({
      company: companyModel.identifier.nullable(),
      contact: contactModel.nullable(),
    }),
    links: schemaModel.links({ self: true }),
  }),
  model: z.object({
    id: z.string(),
    name: z.string(),
    headAccount: z.boolean(),
    companyId: z.string().optional(),
    contactPersonId: z.string().optional(),
  }),
  toModel: (data) => ({
    headAccount: false,
    id: data.id,
    name: data.attributes.name,
    companyId: data.relationships.company?.data?.id,
    contactPersonId: data.relationships.contact.data?.id,
  }),
});
export type AccountModel = Infer<typeof accountModel>;
export type AccountSchema = Infer<typeof accountModel, "schema">;
