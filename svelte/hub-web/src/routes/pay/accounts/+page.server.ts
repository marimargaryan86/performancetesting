import integrationInstances from "integration-instances";
import type { AccountModel } from "models/account";
import { getToken } from "utils/auth";
import type { RequestEvent } from "./$types";

export async function load(
  event: RequestEvent,
): Promise<{ accounts: AccountModel[]; accountsCursor?: string }> {
  const [accounts, accountsCursor] = await integrationInstances.junctionPay.accounts.listAccounts(
    getToken(event),
  );

  return {
    accounts,
    accountsCursor,
  };
}
