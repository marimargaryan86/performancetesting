import { priceModel } from "integration/junction-mobile-api/schemas/price";
import { z } from "zod";
import { orderModel } from "./order";
import schemaModel, { type Infer } from "utils/schema-model";

export const billModel = schemaModel.create({
  schema: z.object({
    id: z.string().uuid(),
    type: z.literal("bills"),
    attributes: z
      .object({
        createdAt: z.date({ coerce: true }).optional(),
        updatedAt: z.date({ coerce: true }).optional(),
        isReconciled: z.boolean().optional(),
        totalAmount: priceModel.schema.optional(),
        reconciledAmount: priceModel.schema.nullable().optional(),
      })
      .optional(),
    relationships: schemaModel
      .relationships({
        order: orderModel.identifier.optional(),
      })
      .optional(),
    links: schemaModel.links({ self: true }),
  }),
  model: z.object({
    id: z.string().uuid(),
    orderId: z.string().uuid().optional(),
    createdAt: z.date({ coerce: true }).optional(),
    updatedAt: z.date({ coerce: true }).optional(),
    isReconciled: z.boolean(),
    amounts: z.object({
      total: priceModel.model.optional(),
      reconciled: priceModel.model.optional(),
    }),
  }),
  toModel: (data) => ({
    id: data.id,
    orderId: data.relationships?.order?.data.id,
    createdAt: data.attributes?.createdAt || undefined,
    updatedAt: data.attributes?.updatedAt || undefined,
    isReconciled: Boolean(data.attributes?.isReconciled),
    amounts: {
      total: data.attributes?.totalAmount
        ? priceModel.toModel(data.attributes.totalAmount)
        : undefined,
      reconciled: data.attributes?.reconciledAmount
        ? priceModel.toModel(data.attributes.reconciledAmount)
        : undefined,
    },
  }),
});
export type BillModel = Infer<typeof billModel>;
export type BillSchema = Infer<typeof billModel, "schema">;
export type BillIdentifier = Infer<typeof billModel, "identifier">;
