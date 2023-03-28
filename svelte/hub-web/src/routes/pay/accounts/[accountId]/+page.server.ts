import type { MoneyModel } from "models/money";
import type { PageServerLoadEvent } from "./$types";
import integrationInstances from "integration-instances";
import { getToken } from "utils/auth";

export async function load(event: PageServerLoadEvent): Promise<{ balances: MoneyModel[] }> {
  const { accountId } = event.params;

  return {
    balances: await integrationInstances.junctionPay.balances.listBalances(
      getToken(event),
      accountId,
    ),
  };
}
