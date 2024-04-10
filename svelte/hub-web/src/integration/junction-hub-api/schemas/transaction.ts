import type { GetOKResponse } from "~/integration/common/types";
import type { Bill } from "./bill";
import type { Company } from "./company";
import type { Conversion } from "./conversion";
import type { IncludedMapping } from "./included";
import { moneyParser, type Money } from "./money";
import type { Specification } from "./__generated__";

export type PaymentType = TransactionSchema["attributes"]["paymentType"];
export type PaymentMethod = TransactionSchema["attributes"]["paymentMethod"];

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
    /** This is the total transaction amount including ticket price and markups */
    totalAmount: Money;
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
    type: PaymentType;
    method: PaymentMethod;
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

export type TransactionSchema = GetOKResponse<
  Specification,
  "/transactions/{transactionId}"
>["data"];

export const transactionParser = {
  toModel: (data: TransactionSchema, included?: IncludedMapping): Transaction => {
    // TODO(2024-04-10): Figure out why this was removed from the API
    // const conversionId = data.relationships?.conversion?.data?.id;
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
        totalAmount: moneyParser.toModel(data.attributes.amounts.totalAmount),
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
      // conversionId,
      // conversion: included?.conversions?.find(({ id }) => id === conversionId),
      billId,
      bill: included?.bills?.find(({ id }) => id === billId),
      payerId,
      payer: included?.companies?.find(({ id }) => id === payerId),
      beneficiaryId,
      beneficiary: included?.companies?.find(({ id }) => id === beneficiaryId),
    };
  },
};
