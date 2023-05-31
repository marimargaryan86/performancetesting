import integrationInstances from "integration-instances";
import type { AccountModel } from "models/account";
import type { PaginatedData } from "models/common";
import { getToken } from "utils/auth";

export function load(event): { accounts: Promise<PaginatedData<AccountModel>> } {
  return {
    accounts: integrationInstances.junctionPay.accounts.listAccounts(getToken(event)),
  };
}
