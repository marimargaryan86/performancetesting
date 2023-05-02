import type { ServerLoadEvent } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { UserJwtSchema } from "integration/junction-pay/schemas/user";
import jwtDecode from "jwt-decode";
import type { CurrencyModel } from "models/money";
import type { UserModel } from "models/user";

export async function load(event: ServerLoadEvent): Promise<{
  user?: UserModel;
  token?: string;
  sessionExpiresAt?: Date;
  currencies: CurrencyModel[];
}> {
  const token = event.cookies.get("session-token");
  let currencies: CurrencyModel[] = [];

  try {
    const user: UserJwtSchema | undefined = token ? jwtDecode(token) : undefined;

    if (token && user) {
      currencies = await integrationInstances.junctionPay.currencies.listCurrencies(token);

      return {
        user: { email: user.user_info.email, id: user.user_info.id, name: "John Smith" },
        token,
        sessionExpiresAt: new Date(user.exp * 1000),
        currencies,
      };
    }
  } catch {
    //
  }

  return { currencies };
}
