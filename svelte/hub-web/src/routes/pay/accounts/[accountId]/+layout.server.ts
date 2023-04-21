import integrationInstances from "integration-instances";
import type { AccountModel } from "models/account";
import { getToken } from "utils/auth";
import type { LayoutServerLoadEvent } from "./$types";

export async function load(event: LayoutServerLoadEvent): Promise<{
  account: AccountModel;
}> {
  return {
    account: await integrationInstances.junctionPay.accounts.getAccount(
      getToken(event),
      event.params.accountId,
    ),
  };
}
