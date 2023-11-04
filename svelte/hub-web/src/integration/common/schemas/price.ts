import { z } from "zod";

export const priceModel = z.object({
  amount: z.number(),
  currency: z.string(),
});

export type Price = z.infer<typeof priceModel>;

export type PriceSchema = {
  amount: string;
  currency: string;
};

export const priceParser = {
  toModel: (data: PriceSchema): Price => ({
    amount: Number(data.amount),
    currency: data.currency,
  }),
  toSchema: (data: Price): PriceSchema => ({
    amount: data.amount.toString(),
    currency: data.currency,
  }),
};

export type PriceBreakdownType =
  | "base-fare"
  | "tax"
  | "reseller-mark-up"
  | "company-mark-up"
  | "service-mark-up";

export type PriceBreakdown = {
  price: Price;
  type: PriceBreakdownType;
};

export type PriceBreakdownSchema = {
  price: PriceSchema;
  breakdownType: PriceBreakdownType;
};

export const priceBreakdownParser = {
  toModel: (data: PriceBreakdownSchema): PriceBreakdown => ({
    price: priceParser.toModel(data.price),
    type: data.breakdownType,
  }),
};
