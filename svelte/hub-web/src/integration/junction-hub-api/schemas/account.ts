import {
  getSchemaModel,
  links,
  relationship,
  type Infer,
} from "integration/common/schema-model.server";
import { z } from "zod";
import { companyModel } from "./company";

export const contactPersonModel = z.object({ id: z.string(), type: z.enum(["contact-persons"]) });

export const accountModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["accounts"]),
    attributes: z.object({
      name: z.string(),
      status: z.string(),
    }),
    relationships: relationship({
      company: companyModel.identifier.optional(),
      contactPerson: contactPersonModel.optional(),
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
      companyId: data.relationships.company?.data.id,
      contactPersonId: data.relationships.contactPerson?.data.id,
    }),
  },
);
export type AccountModel = Infer<typeof accountModel>;
export type AccountSchema = Infer<typeof accountModel, "schema">;
