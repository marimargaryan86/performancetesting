import { getToken } from "utils/auth";
import integrationInstances from "integration-instances";
import type { PriceModel } from "integration/junction-mobile-api/schemas/price";
import type { AccountModel } from "integration/junction-pay/schemas/account.js";

export function load(event): {
  balances: Promise<PriceModel[]>;
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
  async addBalances(event): Promise<{ balances: PriceModel[] }> {
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
