import type { MoneyModel } from "models/money";
import { getToken } from "utils/auth";
import integrationInstances from "integration-instances";

export function load(event): { balances: Promise<MoneyModel[]> } {
  const { accountId } = event.params;

  return {
    balances: integrationInstances.junctionPayApi.balances.listBalances(getToken(event), accountId),
  };
}

export const actions = {
  async addBalances(event): Promise<{ balances: MoneyModel[] }> {
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
