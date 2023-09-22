import { companyModel, type CompanyIdentifier } from "./company";
import { conversionModel, type ConversionIdentifier } from "./conversion";
import { moneyModel } from "./money";
import {
  getSchemaModel,
  links,
  relationship,
  type Infer,
} from "integration/common/schema-model.server";
import { z } from "zod";

const transactionRelationships: z.ZodType<{
  conversion?: { data: ConversionIdentifier | null };
  payer?: { data: CompanyIdentifier };
  beneficiary?: { data: CompanyIdentifier };
}> = relationship({
  conversion: z.lazy(() => conversionModel.identifier.nullable()).optional(),
  payer: z.lazy(() => companyModel.identifier).optional(),
  beneficiary: z.lazy(() => companyModel.identifier).optional(),
});

export const transactionModel = getSchemaModel(
  z.object({
    id: z.string(),
    type: z.enum(["transactions"]),
    attributes: z.object({
      externalReference: z.string(),
      invoiceReference: z.string().optional(),
      createdAt: z.date({ coerce: true }),
      amounts: z.object({
        beneficiary: moneyModel.schema,
        quotation: moneyModel.schema,
        baseConverted: moneyModel.schema,
        salesMargin: moneyModel.schema,
        fxMargin: moneyModel.schema,
        processingMargin: moneyModel.schema,
      }),
      rates: z.object({
        fxQuote: z.number(),
        fxBuffer: z.number(),
        salesMarkup: z.number(),
        fxMarkup: z.number(),
      }),
      paymentType: z.enum(["unspecified", "card", "bank-transfer"]),
      paymentMethod: z.enum(["unspecified", "transactional", "invoice"]),
    }),
    relationships: transactionRelationships,
    links: links(["self"]),
  }),
  z.object({
    id: z.string(),
    bookingId: z.string(),
    createdAt: z.date({ coerce: true }),
    payer: companyModel.model.optional(),
    amounts: z.object({
      beneficiary: moneyModel.model,
      quotation: moneyModel.model,
      salesMargin: moneyModel.model,
    }),
    rates: z.object({
      fxQuote: z.number(),
      fxBuffer: z.number(),
      salesMarkup: z.number(),
      fxMarkup: z.number(),
    }),
    beneficiary: companyModel.model.optional(),
    reference: z.string().optional(),
    payment: z.object({
      type: z.enum(["unspecified", "card", "bank-transfer"]),
      method: z.enum(["unspecified", "transactional", "invoice"]),
    }),
    status: z.enum(["paid", "pending", "cancelled"]),
  }),
  {
    toModel: (data) => ({
      id: data.id,
      bookingId: data.attributes.externalReference,
      beneficiary: undefined,
      payer: undefined,
      createdAt: data.attributes.createdAt,
      amounts: {
        beneficiary: data.attributes.amounts.beneficiary,
        quotation: data.attributes.amounts.quotation,
        salesMargin: data.attributes.amounts.salesMargin,
      },
      rates: {
        fxBuffer: data.attributes.rates.fxBuffer,
        fxMarkup: data.attributes.rates.fxMarkup,
        fxQuote: data.attributes.rates.fxQuote,
        salesMarkup: data.attributes.rates.salesMarkup,
      },
      reference: data.attributes.invoiceReference,
      payment: {
        type: data.attributes.paymentType,
        method: data.attributes.paymentMethod,
      },
      // TODO: Use real status.
      status: "paid" as const,
    }),
  },
);
export type TransactionModel = Infer<typeof transactionModel>;
export type TransactionSchema = Infer<typeof transactionModel, "schema">;
export type TransactionIdentifier = Infer<typeof transactionModel, "identifier">;
export type TransactionStatus = TransactionModel["status"];
