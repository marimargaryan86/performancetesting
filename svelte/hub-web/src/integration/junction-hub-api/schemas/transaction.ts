import schemaModel, { type Infer } from "utils/schema-model";
import { billModel, type BillIdentifier } from "./bill";
import { companyModel, type CompanyIdentifier } from "./company";
import { conversionModel, type ConversionIdentifier } from "./conversion";
import { moneyModel } from "./money";
import { z } from "zod";

const transactionRelationships: z.ZodType<{
  conversion?: { data: ConversionIdentifier | null };
  bill?: { data: BillIdentifier | null };
  payer?: { data: CompanyIdentifier };
  beneficiary?: { data: CompanyIdentifier };
}> = z.lazy(() =>
  schemaModel.relationships({
    conversion: conversionModel.identifier.nullable().optional(),
    bill: billModel.identifier.nullable().optional(),
    payer: companyModel.identifier.optional(),
    beneficiary: companyModel.identifier.optional(),
  }),
);

export const transactionModel = schemaModel.create({
  schema: z.object({
    id: z.string(),
    type: z.literal("transactions"),
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
    relationships: transactionRelationships.optional(),
    links: schemaModel.links({ self: true }),
  }),
  model: z.object({
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
    billId: z.string().uuid().optional(),
    bill: billModel.model.optional(),
    beneficiary: companyModel.model.optional(),
    reference: z.string().optional(),
    payment: z.object({
      type: z.enum(["unspecified", "card", "bank-transfer"]),
      method: z.enum(["unspecified", "transactional", "invoice"]),
    }),
    status: z.enum(["paid", "pending", "cancelled"]),
  }),
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
    billId: data.relationships?.bill?.data?.id,
    bill: undefined,
    reference: data.attributes.invoiceReference,
    payment: {
      type: data.attributes.paymentType,
      method: data.attributes.paymentMethod,
    },
    // TODO: Use real status.
    status: "paid" as const,
  }),
});
export type TransactionModel = Infer<typeof transactionModel>;
export type TransactionSchema = Infer<typeof transactionModel, "schema">;
export type TransactionIdentifier = Infer<typeof transactionModel, "identifier">;
export type TransactionStatus = TransactionModel["status"];
