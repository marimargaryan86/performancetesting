import type { Account, AccountSchema } from "./account";
import type { Currency, CurrencySchema } from "./currency";
import type { IncludedMapping } from "./included";

export type Balance = {
  id: string;
  amount: number;
  accountId: string;
  account?: Account;
  currencyId: string;
  currency?: Currency;
};

export type BalanceAdd = Pick<Balance, "currencyId">;

export type BalanceSchema = {
  id: string;
  type: "balances";
  attributes: {
    amount: number;
  };
  relationships: {
    account: { data: Pick<AccountSchema, "id" | "type"> };
    currency: { data: Pick<CurrencySchema, "id" | "type"> };
  };
};

export type BalanceAddSchema = Pick<BalanceSchema, "type"> & {
  relationships: Pick<BalanceSchema["relationships"], "currency">;
};

export const balanceParser = {
  toModel: (data: BalanceSchema, included?: IncludedMapping): Balance => {
    const accountId = data.relationships.account.data.id;
    const currencyId = data.relationships.currency.data.id;

    return {
      id: data.id,
      amount: data.attributes.amount,
      accountId,
      account: included?.accounts?.find(({ id }) => id === accountId),
      currencyId,
      currency: included?.currencies?.find(({ code }) => code === currencyId),
    };
  },
  toAddSchema: (data: BalanceAdd): BalanceAddSchema => ({
    type: "balances",
    relationships: { currency: { data: { id: data.currencyId, type: "currencies" } } },
  }),
};
