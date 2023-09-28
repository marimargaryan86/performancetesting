import { getSchemaModel, links, type Infer } from "integration/common/schema-model.server";
import { priceModel } from "integration/junction-mobile-api/schemas/price";
import { z } from "zod";

export const moneyModel = getSchemaModel(
  z.object({
    currency: z.string(),
    amount: z.number(),
  }),
  priceModel.model,
);

export const currencyModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["currencies"]),
    attributes: z.object({
      name: z.string(),
      minorUnits: z.number(),
    }),
    links: links(["self"]),
  }),
  z.object({
    name: z.string(),
    code: z.string(),
    minorUnits: z.number(),
  }),
  {
    toModel: (data) => ({
      name: data.attributes.name,
      code: data.id,
      minorUnits: data.attributes.minorUnits,
    }),
  },
);
export type CurrencyModel = Infer<typeof currencyModel>;
export type CurrencySchema = Infer<typeof currencyModel, "schema">;
