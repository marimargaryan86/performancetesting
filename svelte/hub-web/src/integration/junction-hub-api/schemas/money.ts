import { priceModel } from "integration/junction-mobile-api/schemas/price";
import schemaModel, { type Infer } from "utils/schema-model";
import { z } from "zod";

export const moneyModel = schemaModel.create({
  schema: z.object({
    currency: z.string(),
    amount: z.number(),
  }),
  model: priceModel.model,
});

export const currencyModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.literal("currencies"),
    attributes: z.object({
      name: z.string(),
      minorUnits: z.number(),
    }),
    links: schemaModel.links({ self: true }),
  }),
  model: z.object({
    name: z.string(),
    code: z.string(),
    minorUnits: z.number(),
  }),
  toModel: (data) => ({
    name: data.attributes.name,
    code: data.id,
    minorUnits: data.attributes.minorUnits,
  }),
});
export type CurrencyModel = Infer<typeof currencyModel>;
export type CurrencySchema = Infer<typeof currencyModel, "schema">;
