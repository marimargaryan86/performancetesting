import type { RelationshipSchema } from "./common";
import type { CompanyIdentifierSchema } from "./company";
import type { ConversionIdentifierSchema } from "./conversion";
import type { MoneySchema } from "./money";

export interface TransactionIdentifierSchema {
  id: string;
  type: "transactions";
}

export interface TransactionSchema extends TransactionIdentifierSchema {
  attributes: {
    externalReference: string;
    parentExternalReference: string;
    createdAt: string;
    amounts: {
      beneficiary: MoneySchema;
      quotation: MoneySchema;
      baseConverted: MoneySchema;
      salesMargin: MoneySchema;
      fxMargin: MoneySchema;
      fxProviderMargin: MoneySchema;
    };
    rates: {
      fxQuote: number;
      fxBuffer: number;
      salesMarkup: number;
      fxMarkup: number;
    };
  };
  relationships: {
    conversion: RelationshipSchema<ConversionIdentifierSchema>;
    payer: RelationshipSchema<CompanyIdentifierSchema>;
    beneficiary: RelationshipSchema<CompanyIdentifierSchema>;
  };
  links: { self: string };
}

export interface ListTransactionsResponseSchema {
  data: TransactionSchema[];
  links: { next: string };
}
