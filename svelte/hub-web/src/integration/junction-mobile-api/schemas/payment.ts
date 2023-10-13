import { z } from "zod";
import { priceModel } from "./price";
import schemaModel, { type Infer } from "utils/schema-model";

export const paymentIntentModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.enum(["payments"]),
    attributes: z.object({
      clientSecret: z.string(),
      ephemeralKey: z.string().optional(),
      customerId: z.string().optional(),
    }),
  }),
  model: z.object({
    id: z.string(),
    clientSecret: z.string(),
    ephemeralKey: z.string().optional(),
    customerId: z.string().optional(),
  }),
  toModel: (data) => ({ ...data, ...data.attributes }),
});
export type PaymentIntentModel = Infer<typeof paymentIntentModel>;
export type PaymentIntentSchema = Infer<typeof paymentIntentModel, "schema">;

export const createPaymentIntentModel = schemaModel.create({
  schema: z.object({
    type: z.enum(["payments"]),
    attributes: priceModel.schema,
  }),
  model: priceModel.model,
  toSchema: (data) =>
    ({
      type: "payments",
      attributes: priceModel.toSchema(data),
    } as const),
});
