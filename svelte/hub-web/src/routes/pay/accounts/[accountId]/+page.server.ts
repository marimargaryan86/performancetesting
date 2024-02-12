import integrationInstances from "~/integration-instances";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";

export async function load(event): Promise<{
  balances: HubSchemas.Balance[];
  account: HubSchemas.Account;
}> {
  const { accountId } = event.params;
  const session = event.locals.session;

  const [account, balances] = await Promise.all([
    integrationInstances.junctionHubApi.accounts.get({ session, id: accountId }),
    integrationInstances.junctionHubApi.balances.find({ session, accountId }),
  ]);

  return { account, balances };
}
