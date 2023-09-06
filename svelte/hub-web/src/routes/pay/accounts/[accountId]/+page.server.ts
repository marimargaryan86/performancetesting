import { getToken } from "utils/auth";
import integrationInstances from "integration-instances";
import type { priceModel } from "integration/junction-mobile-api/schemas/price";
import type { Infer } from "integration/junction-mobile-api/schema-model.server";
import type { AccountModel } from "models/account";

export function load(event): {
  balances: Promise<Infer<typeof priceModel>[]>;
  account: Promise<AccountModel>;
} {
  const { accountId } = event.params;
  const token = getToken(event);

  return {
    account: integrationInstances.junctionPayApi.accounts.getAccount(token, accountId),
    balances: integrationInstances.junctionPayApi.balances.listBalances(token, accountId),
  };
}

export const actions = {
  async addBalances(event): Promise<{ balances: Infer<typeof priceModel>[] }> {
    const { accountId } = event.params;
    const formData = await event.request.formData();
    const jsonData = JSON.parse(formData.get("json")?.toString() ?? "{}") as {
      currencyCodes?: string[];
    };

    if (!jsonData.currencyCodes) {
      return { balances: [] };
    }

    return {
      balances: await Promise.all(
        jsonData.currencyCodes.map((currencyCode) =>
          integrationInstances.junctionPayApi.balances.addBalance(
            getToken(event),
            accountId,
            currencyCode,
          ),
        ),
      ),
    };
  },
};
