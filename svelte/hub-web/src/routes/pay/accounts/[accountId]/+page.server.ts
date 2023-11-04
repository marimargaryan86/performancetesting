import { getSession } from "utils/auth";
import integrationInstances from "integration-instances";
import type { Account } from "integration/junction-hub-api/schemas/account";
import type { Balance } from "integration/junction-hub-api/schemas/balance";

export async function load(event): Promise<{
  balances: Balance[];
  account: Account;
}> {
  const { accountId } = event.params;
  const session = getSession(event);

  const [account, balances] = await Promise.all([
    integrationInstances.junctionHubApi.accounts.getAccount({ session, id: accountId }),
    integrationInstances.junctionHubApi.balances.listBalances({ session, accountId }),
  ]);

  return { account, balances };
}

export const actions = {
  async addBalances(event): Promise<{ balances: Balance[] }> {
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
        jsonData.currencyCodes.map((currencyId) =>
          integrationInstances.junctionHubApi.balances.addBalance({
            session: getSession(event),
            accountId,
            data: { currencyId },
          }),
        ),
      ),
    };
  },
};
