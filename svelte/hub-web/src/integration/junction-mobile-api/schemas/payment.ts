import { z } from "zod";
import { getSchemaModel, type Infer } from "../../common/schema-model.server";
import { priceModel } from "./price";

export const paymentIntentModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["payments"]),
    attributes: z.object({
      clientSecret: z.string(),
      ephemeralKey: z.string().optional(),
      customerId: z.string().optional(),
    }),
  }),
  z.object({
    id: z.string(),
    clientSecret: z.string(),
    ephemeralKey: z.string().optional(),
    customerId: z.string().optional(),
  }),
  {
    toModel: (data) => ({ ...data, ...data.attributes }),
  },
);
export type PaymentIntentModel = Infer<typeof paymentIntentModel>;
export type PaymentIntentSchema = Infer<typeof paymentIntentModel, "schema">;

export const createPaymentIntentModel = getSchemaModel(
  z.object({
    type: z.enum(["payments"]),
    attributes: priceModel.schema,
  }),
  priceModel.model,
  {
    toSchema: (data) => ({
      type: "payments" as const,
      attributes: priceModel.toSchema(data),
    }),
  },
);
