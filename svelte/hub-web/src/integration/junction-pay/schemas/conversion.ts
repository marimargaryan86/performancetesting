import { moneyModel } from "./money";
import { transactionModel, type TransactionIdentifier, type TransactionModel } from "./transaction";
import {
  getSchemaModel,
  links,
  relationship,
  type Infer,
} from "integration/common/schema-model.server";
import { z } from "zod";

const conversionRelationships: z.ZodType<{
  transactions: { data: TransactionIdentifier };
}> = relationship({
  transactions: z.lazy(() => transactionModel.identifier),
});

const conversionModelBase = z.object({
  id: z.string(),
  createdAt: z.date({ coerce: true }).optional(),
  settledAt: z.date({ coerce: true }).optional(),
  sellAmount: moneyModel.model.optional(),
  buyAmount: moneyModel.model.optional(),
  executedRate: z.number().optional(),
  fxDelta: z.number().optional(),
  fxStatus: z.enum(["executed", "unspecified", "failed"]).optional(),
});

const conversionModelExt: z.ZodType<
  z.infer<typeof conversionModelBase> & { transaction?: TransactionModel }
> = conversionModelBase.extend({
  transaction: z.lazy(() => transactionModel.model).optional(),
});

export const conversionModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["conversions"]),
    attributes: z.object({
      createdAt: z.date({ coerce: true }).optional(),
      settledAt: z.date({ coerce: true }).optional(),
      sellAmount: moneyModel.schema.optional(),
      buyAmount: moneyModel.schema.optional(),
      executedRate: z.number().optional(),
      fxDelta: z.number().nullable().optional(),
      fxStatus: z.enum(["unspecified", "executed", "failed"]).optional(),
    }),
    relationships: conversionRelationships.optional(),
    links: links(["self"]),
  }),
  conversionModelExt,
  {
    toModel: (data) => ({
      id: data.id,
      buyAmount: data.attributes.buyAmount,
      createdAt: data.attributes.createdAt,
      executedRate: data.attributes.executedRate,
      fxDelta: data.attributes.fxDelta ?? undefined,
      fxStatus: data.attributes.fxStatus,
      sellAmount: data.attributes.sellAmount,
      settledAt: data.attributes.settledAt,
      transaction: undefined,
    }),
  },
);
export type ConversionModel = Infer<typeof conversionModel>;
export type ConversionSchema = Infer<typeof conversionModel, "schema">;
export type ConversionIdentifier = Infer<typeof conversionModel, "identifier">;
export type ConversionStatus = NonNullable<ConversionModel["fxStatus"]>;
