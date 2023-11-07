import { redirect } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { Currency } from "integration/junction-hub-api/schemas/currency";
import type { CountryModel } from "models/location";
import type { UserModel } from "models/user";
import routeConfig from "routeConfig";
import { deleteSession, getSession } from "utils/auth";

export async function load(event): Promise<{
  user?: UserModel;
  sessionExpiresAt?: Date;
  currencies: Map<string, Currency>;
  countries: Map<string, CountryModel>;
}> {
  const user = event.locals.user;

  if (!user) {
    return { currencies: new Map(), countries: new Map() };
  }

  try {
    const session = getSession(event);
    const currencies = await integrationInstances.junctionHubApi.currencies.find({ session });

    return {
      user,
      sessionExpiresAt: event.locals.sessionExpiresAt,
      currencies: new Map(currencies.data.map((currency) => [currency.code, currency])),
      countries: integrationInstances.common.countries.findCountries(),
    };
  } catch {
    deleteSession(event);

    throw redirect(303, routeConfig.routes.login.root);
  }
}
