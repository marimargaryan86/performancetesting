import integrationInstances from "integration-instances";
import type { AccountModel } from "models/account";
import { getToken } from "utils/auth";

export function load(event): { account: Promise<AccountModel> } {
  return {
    account: integrationInstances.junctionPayApi.accounts.getAccount(
      getToken(event),
      event.params.accountId,
    ),
  };
}
