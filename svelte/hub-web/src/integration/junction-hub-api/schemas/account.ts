import {
  getSchemaModel,
  links,
  relationship,
  type Infer,
} from "integration/common/schema-model.server";
import { z } from "zod";
import { companyModel } from "./company";

export const contactModel = z.object({ id: z.string(), type: z.enum(["contacts"]) });

export const accountModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["accounts"]),
    attributes: z.object({
      name: z.string(),
      status: z.string(),
    }),
    relationships: relationship({
      company: companyModel.identifier.nullable(),
      contact: contactModel.nullable(),
    }),
    links: links(["self"]),
  }),
  z.object({
    id: z.string(),
    name: z.string(),
    headAccount: z.boolean(),
    companyId: z.string().optional(),
    contactPersonId: z.string().optional(),
  }),
  {
    toModel: (data) => ({
      headAccount: false,
      id: data.id,
      name: data.attributes.name,
      companyId: data.relationships.company?.data?.id,
      contactPersonId: data.relationships.contact.data?.id,
    }),
  },
);
export type AccountModel = Infer<typeof accountModel>;
export type AccountSchema = Infer<typeof accountModel, "schema">;
