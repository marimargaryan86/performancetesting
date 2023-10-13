import { accountModel } from "./account";
import { priceModel } from "integration/junction-mobile-api/schemas/price";
import { z } from "zod";
import { currencyModel } from "./money";
import schemaModel, { type Infer } from "utils/schema-model";

export const balanceModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.enum(["balances"]),
    attributes: z.object({ amount: z.number() }),
    relationships: schemaModel.relationships({
      account: accountModel.identifier,
      currency: currencyModel.identifier,
    }),
  }),
  model: priceModel.model,
  toModel: (data) => ({
    amount: data.attributes.amount,
    currency: data.relationships.currency.data.id,
  }),
});
export type BalanceSchema = Infer<typeof balanceModel, "schema">;

export const createBalanceModel = schemaModel.create({
  schema: z.object({
    type: z.enum(["balances"]),
    relationships: schemaModel.relationships({
      currency: z.object({
        id: z.string(),
        type: z.enum(["currencies"]),
      }),
    }),
  }),
  model: z.object({ currencyCode: z.string() }),
  toSchema: (data) => ({
    type: "balances" as const,
    relationships: {
      currency: { data: { id: data.currencyCode, type: "currencies" as const } },
    },
  }),
});
