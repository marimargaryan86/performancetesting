import type { Conversion, ConversionSchema } from "./conversion";
import type { IncludedMapping } from "./included";
import { moneyParser, type Money, type MoneySchema } from "./money";
import type { Transaction, TransactionSchema } from "./transaction";

export type RefundPosition = {
  id: string;
  total?: Money;
};

export type RefundPositionSchema = {
  id: string;
  type: "refund-position";
  attributes: {
    refundPosition?: MoneySchema;
  };
};

export const refundPositionParser = {
  toModel: (data: RefundPositionSchema): RefundPosition => ({
    id: data.id,
    total: data.attributes.refundPosition
      ? moneyParser.toModel(data.attributes.refundPosition)
      : undefined,
  }),
};

export type Refund = {
  id: string;
  status: "pending" | "executed";
  received: boolean;
  note: string;
  refunded: {
    us: Money;
    usInPayerCurrency?: Money;
    reseller: Money;
  };
  invoiceReference: string;
  transactionId?: string;
  transaction?: Transaction;
  conversionId?: string;
  conversion?: Conversion;
  refundPosition?: RefundPosition;
};

export type RefundPut = Pick<Refund, "received" | "note" | "invoiceReference" | "transactionId"> & {
  refunded: Pick<Refund["refunded"], "reseller" | "us">;
};

export type RefundSchema = {
  id: string;
  type: "refunds";
  attributes: {
    status: "pending" | "executed";
    refundReceived: boolean;
    note: string;
    refundedUs: MoneySchema;
    refundedUsInPayerCurrency?: MoneySchema | null;
    refundedReseller: MoneySchema;
    invoiceReference: string;
  };
  relationships: {
    transaction: { data?: Pick<TransactionSchema, "id" | "type"> };
    conversion: { data?: Pick<ConversionSchema, "id" | "type"> | null };
    refundPosition?: RefundPositionSchema;
  };
  links: { self: string };
};

export type RefundPutSchema = Pick<RefundSchema, "type"> & {
  attributes: Omit<RefundSchema["attributes"], "status" | "refundedUsInPayerCurrency">;
  relationships: Pick<RefundSchema["relationships"], "transaction">;
};

export const refundParser = {
  toModel: (data: RefundSchema, included?: IncludedMapping): Refund => {
    const transactionId = data.relationships.transaction.data?.id ?? undefined;
    const conversionId = data.relationships.conversion.data?.id ?? undefined;
    const refundPosition = data.relationships.refundPosition;

    return {
      id: data.id,
      status: data.attributes.status,
      received: data.attributes.refundReceived,
      note: data.attributes.note,
      refunded: {
        us: moneyParser.toModel(data.attributes.refundedUs),
        usInPayerCurrency: data.attributes.refundedUsInPayerCurrency
          ? moneyParser.toModel(data.attributes.refundedUsInPayerCurrency)
          : undefined,
        reseller: moneyParser.toModel(data.attributes.refundedReseller),
      },
      invoiceReference: data.attributes.invoiceReference,
      transactionId,
      transaction: included?.transactions?.find(({ id }) => id === transactionId),
      conversionId,
      conversion: included?.conversions?.find(({ id }) => id === conversionId),
      refundPosition: refundPosition ? refundPositionParser.toModel(refundPosition) : undefined,
    };
  },
  toPutSchema: (data: RefundPut): RefundPutSchema => ({
    type: "refunds",
    attributes: {
      refundReceived: data.received,
      note: data.note,
      refundedUs: data.refunded.us,
      refundedReseller: data.refunded.reseller,
      invoiceReference: data.invoiceReference,
    },
    relationships: {
      transaction: {
        data: data.transactionId ? { id: data.transactionId, type: "transactions" } : undefined,
      },
    },
  }),
};
