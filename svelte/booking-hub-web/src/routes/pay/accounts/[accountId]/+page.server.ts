import type { MoneyModel } from "models/money";
import integrationInstances from "integration-instances";
import { getToken } from "utils/auth";

export function load(event): { balances: Promise<MoneyModel[]> } {
  const { accountId } = event.params;

  return {
    balances: integrationInstances.junctionPay.balances.listBalances(getToken(event), accountId),
  };
}
