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
    beneficiaryAmount: MoneySchema;
    offerAmount: MoneySchema;
    convertedBeneficiaryAmount: MoneySchema;
    bufferAmount: MoneySchema;
    salesAmount: MoneySchema;
    exchangeRate: number;
    bufferRate: number;
    salesRate: number;
  };
  relationships: {
    conversion: RelationshipSchema<ConversionIdentifierSchema>;
    payer: RelationshipSchema<CompanyIdentifierSchema>;
    beneficiary: RelationshipSchema<CompanyIdentifierSchema>;
  };
}

export interface ListTransactionsResponseSchema {
  data: TransactionSchema[];
  links: { next: string };
}
