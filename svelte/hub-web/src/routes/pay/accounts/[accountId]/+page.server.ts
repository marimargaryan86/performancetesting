import { getSession } from "utils/auth";
import integrationInstances from "integration-instances";
import type { PriceModel } from "integration/junction-mobile-api/schemas/price";
import type { AccountModel } from "integration/junction-hub-api/schemas/account";

export function load(event): {
  balances: Promise<PriceModel[]>;
  account: Promise<AccountModel>;
} {
  const { accountId } = event.params;
  const session = getSession(event);

  return {
    account: integrationInstances.junctionPayApi.accounts.getAccount({ session, id: accountId }),
    balances: integrationInstances.junctionPayApi.balances.listBalances({ session, accountId }),
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
          integrationInstances.junctionPayApi.balances.addBalance({
            session: getSession(event),
            accountId,
            currencyCode,
          }),
        ),
      ),
    };
  },
};
