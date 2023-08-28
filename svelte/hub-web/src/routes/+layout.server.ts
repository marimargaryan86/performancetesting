import { redirect } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { CountryModel } from "models/location";
import type { CurrencyModel } from "models/money";
import type { UserModel } from "models/user";
import routeConfig from "routeConfig";

export async function load(event): Promise<{
  user?: {
    data: UserModel;
    token: string;
    sessionExpiresAt: Date;
  };
  currencies: Map<string, CurrencyModel>;
  countries: Map<string, CountryModel>;
}> {
  const user = event.locals.user;

  if (!user) {
    return { currencies: new Map(), countries: new Map() };
  }

  try {
    return {
      user,
      currencies: await integrationInstances.junctionPayApi.currencies.listCurrencies(user.token),
      countries: integrationInstances.common.countries.findCountries(),
    };
  } catch {
    event.cookies.delete("session-token", { path: "/" });

    throw redirect(303, routeConfig.login);
  }
}
