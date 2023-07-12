import type { RelationshipSchema } from "./common";
import type { MoneySchema } from "./money";
import type { TransactionIdentifierSchema, TransactionSchema } from "./transaction";

export interface ConversionIdentifierSchema {
  id: string;
  type: "conversions";
}

export const conversionStatus = ["unspecified", "executed", "failed"] as const;

export type ConversionStatus = (typeof conversionStatus)[number];

export interface ConversionSchema extends ConversionIdentifierSchema {
  attributes: {
    createdAt: string | null;
    settledAt: string | null;
    sellAmount: MoneySchema | null;
    buyAmount: MoneySchema;
    executedRate: number;
    fxDelta: number | null;
    fxStatus: ConversionStatus;
  };
  relationships?: {
    transactions: RelationshipSchema<TransactionIdentifierSchema>;
  };
  links: { self: string };
}

export interface GetConversionDetailsResponseSchema {
  data: ConversionSchema;
  included: TransactionSchema[];
}

export interface ListConversionDetailsResponseSchema {
  data: ConversionSchema[];
  included: TransactionSchema[];
  links: { next: string };
}
