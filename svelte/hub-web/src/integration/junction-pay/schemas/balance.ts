import { accountModel } from "./account";
import { getSchemaModel, relationship, type Infer } from "integration/common/schema-model.server";
import { priceModel } from "integration/junction-mobile-api/schemas/price";
import { z } from "zod";
import { currencyModel } from "./money";

export const balanceModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["balances"]),
    attributes: z.object({ amount: z.number() }),
    relationships: relationship({
      account: accountModel.identifier,
      currency: currencyModel.identifier,
    }),
  }),
  priceModel.model,
  {
    toModel: (data) => ({
      amount: data.attributes.amount,
      currency: data.relationships.currency.data.id,
    }),
  },
);
export type BalanceSchema = Infer<typeof balanceModel, "schema">;

export const createBalanceModel = getSchemaModel(
  z.object({
    type: z.enum(["balances"]),
    relationships: relationship({
      currency: z.object({
        id: z.string(),
        type: z.enum(["currencies"]),
      }),
    }),
  }),
  z.object({ currencyCode: z.string() }),
  {
    toSchema: (data) => ({
      type: "balances" as const,
      relationships: {
        currency: { data: { id: data.currencyCode, type: "currencies" as const } },
      },
    }),
  },
);
