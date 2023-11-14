import type { Bill, BillSchema } from "./bill";
import type { Company, CompanySchema } from "./company";
import type { Conversion, ConversionSchema } from "./conversion";
import type { IncludedMapping } from "./included";
import { moneyParser, type Money, type MoneySchema } from "./money";

export type Transaction = {
  id: string;
  externalReference: string;
  invoiceReference?: string;
  createdAt: Date;
  amounts: {
    /** This is how much Junction PAY will need to pay out */
    beneficiary: Money;
    /** The amount that Junction PAY will be owed */
    quotation: Money;
    /** The amount Junction PAY will need to collect in the payers currency to cover what Junction PAY owes to a beneficiary */
    baseConverted: Money;
  };
  fx: {
    /** The monetary value of the fx markup for a specific transaction for Junction PAY */
    margin: Money;
    /** The percentage Junction PAY adds to foreign exchange */
    markup: number;
    /** The FX rate Junction PAY provided during the quotation call */
    quote: number;
    /** The amount the exchange rate can move between quotation and transaction before Junction PAY loose money on the trade */
    buffer: number;
  };
  processing: {
    /** The monetary value of the provider markup for a specific transaction */
    margin: Money;
    /** The percentage incurred by the business */
    markup: number;
  };
  sales: {
    /** The monetary value of the sales markup for a specific transaction */
    margin: Money;
    /** The percentage Junction PAY adds as a sales fee */
    markup: number;
  };
  payment: {
    type: "unspecified" | "card" | "bank-transfer";
    method: "unspecified" | "transactional" | "invoice";
  };
  conversionId?: string;
  conversion?: Conversion;
  billId?: string;
  bill?: Bill;
  payerId?: string;
  payer?: Company;
  beneficiaryId?: string;
  beneficiary?: Company;
};

export type TransactionSchema = {
  id: string;
  type: "transactions";
  attributes: {
    externalReference: string;
    invoiceReference?: string;
    createdAt: string;
    amounts: {
      beneficiary: MoneySchema;
      quotation: MoneySchema;
      baseConverted: MoneySchema;
      salesMargin: MoneySchema;
      fxMargin: MoneySchema;
      processingMargin: MoneySchema;
    };
    rates: {
      fxQuote: number;
      fxBuffer: number;
      salesMarkup: number;
      fxMarkup: number;
      processingMarkup: number;
    };
    paymentType: "unspecified" | "card" | "bank-transfer";
    paymentMethod: "unspecified" | "transactional" | "invoice";
  };
  relationships?: {
    conversion?: { data: Pick<ConversionSchema, "id" | "type"> | null };
    bill?: { data: Pick<BillSchema, "id" | "type"> | null };
    payer?: { data: Pick<CompanySchema, "id" | "type"> };
    beneficiary?: { data: Pick<CompanySchema, "id" | "type"> };
  };
  links: { self: string };
};

export const transactionParser = {
  toModel: (data: TransactionSchema, included?: IncludedMapping): Transaction => {
    const conversionId = data.relationships?.conversion?.data?.id;
    const billId = data.relationships?.bill?.data?.id;
    const payerId = data.relationships?.payer?.data.id;
    const beneficiaryId = data.relationships?.beneficiary?.data.id;

    return {
      id: data.id,
      externalReference: data.attributes.externalReference,
      invoiceReference: data.attributes.invoiceReference,
      createdAt: new Date(data.attributes.createdAt),
      amounts: {
        beneficiary: moneyParser.toModel(data.attributes.amounts.beneficiary),
        quotation: moneyParser.toModel(data.attributes.amounts.quotation),
        baseConverted: moneyParser.toModel(data.attributes.amounts.baseConverted),
      },
      fx: {
        margin: moneyParser.toModel(data.attributes.amounts.fxMargin),
        markup: data.attributes.rates.fxMarkup,
        buffer: data.attributes.rates.fxBuffer,
        quote: data.attributes.rates.fxQuote,
      },
      processing: {
        margin: moneyParser.toModel(data.attributes.amounts.processingMargin),
        markup: data.attributes.rates.processingMarkup,
      },
      sales: {
        margin: moneyParser.toModel(data.attributes.amounts.salesMargin),
        markup: data.attributes.rates.salesMarkup,
      },
      payment: {
        type: data.attributes.paymentType,
        method: data.attributes.paymentMethod,
      },
      conversionId,
      conversion: included?.conversions?.find(({ id }) => id === conversionId),
      billId,
      bill: included?.bills?.find(({ id }) => id === billId),
      payerId,
      payer: included?.companies?.find(({ id }) => id === payerId),
      beneficiaryId,
      beneficiary: included?.companies?.find(({ id }) => id === beneficiaryId),
    };
  },
};
