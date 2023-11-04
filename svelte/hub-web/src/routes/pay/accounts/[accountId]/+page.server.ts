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
    integrationInstances.junctionHubApi.accounts.get({ session, id: accountId }),
    integrationInstances.junctionHubApi.balances.find({ session, accountId }),
  ]);

  return { account, balances };
}
