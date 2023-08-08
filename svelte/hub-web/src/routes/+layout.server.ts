import type { MaybePromise } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { CountryModel } from "models/location";
import type { CurrencyModel } from "models/money";
import type { UserModel } from "models/user";

export function load(event): {
  user?: {
    data: UserModel;
    token: string;
    sessionExpiresAt: Date;
  };
  currencies: MaybePromise<Map<string, CurrencyModel>>;
  countries: Map<string, CountryModel>;
} {
  const user = event.locals.user;

  if (!user) {
    return { currencies: new Map(), countries: new Map() };
  }

  return {
    user,
    currencies: integrationInstances.junctionPay.currencies.listCurrencies(user.token),
    countries: integrationInstances.common.countries.findCountries(),
  };
}
