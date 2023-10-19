import { z } from "zod";
import { moneyModel } from "./money";
import schemaModel, { type Infer } from "utils/schema-model";

export const addressDetailsModel = schemaModel.create({
  schema: z.object({
    addressLines: z.array(z.string()),
    countryCode: z.string(),
    postalCode: z.string(),
    city: z.string(),
  }),
  model: z.object({}),
});

export const companyModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.literal("companies"),
    attributes: z.object({
      name: z.string().optional(),
      address: addressDetailsModel.schema.optional(),
      fxMarkup: z.number().optional(),
      processingMarkup: z.number().optional(),
      salesMarkup: z.number().optional(),
      resellerMarkups: z.array(moneyModel.schema).optional(),
      paymentType: z.enum(["unspecified", "transactional", "invoice"]).optional(),
      resellerProviders: z.array(z.string().uuid()).optional(),
      companyType: z.enum(["unspecified", "provider", "reseller"]).optional(),
      defaultCurrenzy: z.string().optional(),
    }),
  }),
  model: z.object({
    id: z.string(),
    name: z.string().optional(),
  }),
  toModel: (data) => ({
    id: data.id,
    name: data.attributes.name,
  }),
});
export type CompanyModel = Infer<typeof companyModel>;
export type CompanySchema = Infer<typeof companyModel, "schema">;
export type CompanyIdentifier = Infer<typeof companyModel, "identifier">;
