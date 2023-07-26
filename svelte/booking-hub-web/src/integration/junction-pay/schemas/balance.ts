import type { AccountIdentifierSchema } from "./account";
import type { RelationshipSchema } from "./common";
import type { CurrencyIdentifierSchema } from "./money";

export interface BalanceIdentifierSchema {
  id: string;
  type: "balances";
}

export interface BalanceSchema extends BalanceIdentifierSchema {
  attributes: { amount: number };
  relationships: {
    account: RelationshipSchema<AccountIdentifierSchema>;
    currency: RelationshipSchema<CurrencyIdentifierSchema>;
  };
}

export interface ListBalancesResponseSchema {
  data: BalanceSchema[];
}

export interface AddBalanceResponseSchema {
  data: BalanceSchema;
}
