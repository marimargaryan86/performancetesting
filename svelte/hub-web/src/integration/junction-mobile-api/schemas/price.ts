import schemaModel, { type Infer } from "utils/schema-model";
import { z } from "zod";

export const priceModel = schemaModel.create({
  schema: z.object({
    currency: z.string(),
    amount: z.string({ coerce: true }),
  }),
  model: z.object({
    currency: z.string(),
    amount: z.number(),
  }),
  toModel: (data) => ({
    amount: Number(data.amount),
    currency: data.currency,
  }),
  toSchema: (data) => ({
    amount: data.amount.toString(),
    currency: data.currency,
  }),
});
export type PriceModel = Infer<typeof priceModel>;
export type PriceSchema = Infer<typeof priceModel, "schema">;

export const priceBreakdownType = z.enum([
  "base-fare",
  "tax",
  "reseller-mark-up",
  "company-mark-up",
  "service-mark-up",
]);
export type PriceBreakdownType = z.infer<typeof priceBreakdownType>;

export const priceBreakdownModel = schemaModel.create({
  schema: z.object({
    price: priceModel.schema,
    breakdownType: priceBreakdownType,
  }),
  model: z.object({
    price: priceModel.model,
    type: priceBreakdownType,
  }),
  toModel: (data) => ({
    type: data.breakdownType,
    price: priceModel.toModel(data.price),
  }),
  toSchema: (data) => ({
    breakdownType: data.type,
    price: priceModel.toSchema(data.price),
  }),
});
export type PriceBreakdownModel = Infer<typeof priceBreakdownModel>;
