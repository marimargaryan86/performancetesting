import type { MaybePromise } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { CurrencyModel } from "models/money";
import type { UserModel } from "models/user";

export function load(event): {
  user?: {
    data: UserModel;
    token: string;
    sessionExpiresAt: Date;
  };
  currencies: MaybePromise<CurrencyModel[]>;
} {
  const user = event.locals.user;

  if (!user) {
    return { currencies: [] };
  }

  return {
    user,
    currencies: integrationInstances.junctionPay.currencies.listCurrencies(user.token),
  };
}
