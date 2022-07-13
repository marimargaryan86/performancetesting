import type { Identifier } from "./base-schemas";

export type BalanceIdentifier = Identifier & { type: "balances" };

export type BalancesResponse = {
  data: (Identifier & {
    attributes: {
      amount: number;
    };
    relationships: {
      currency: {
        data: Identifier;
      };
    };
  })[];
  links: {
    next: string;
  };
};
