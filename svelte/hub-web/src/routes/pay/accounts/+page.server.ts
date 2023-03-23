import integrationInstances from "integration-instances";
import type { AccountModel } from "models/account";
import { getToken } from "utils/auth";
import type { RequestEvent } from "./$types";

export async function load(event: RequestEvent): Promise<{ accounts: AccountModel[] }> {
  return {
    accounts: await integrationInstances.junctionPay.accounts.listAccounts(getToken(event)),
  };
}
