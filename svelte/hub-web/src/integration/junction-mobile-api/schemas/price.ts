import { z } from "zod";
import { getSchemaModel, type Infer } from "../schema-model.server";

export const priceModel = getSchemaModel(
  z.object({
    currency: z.string(),
    amount: z.string(),
  }),
  z.object({
    currency: z.string(),
    amount: z.number(),
  }),
  {
    toModel: (data) => ({
      amount: Number(data.amount),
      currency: data.currency,
    }),
    toSchema: (data) => ({
      amount: data.amount.toString(),
      currency: data.currency,
    }),
  },
);
export type PriceModel = Infer<typeof priceModel>;
export type PriceSchema = Infer<typeof priceModel, "schema">;

export const priceBreakdownType = z.enum([
  "base-fare",
  "tax",
  "reseller-mark-up",
  "company-mark-up",
  "service-mark-up",
]);

export const priceBreakdownModel = getSchemaModel(
  z.object({
    price: priceModel.schema,
    breakdownType: priceBreakdownType,
  }),
  z.object({
    price: priceModel.model,
    type: priceBreakdownType,
  }),
  {
    toModel: (data) => ({
      type: data.breakdownType,
      price: priceModel.toModel(data.price),
    }),
    toSchema: (data) => ({
      breakdownType: data.type,
      price: priceModel.toSchema(data.price),
    }),
  },
);
export type PriceBreakdownModel = Infer<typeof priceBreakdownModel>;
