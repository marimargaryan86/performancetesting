import { mockAccounts } from "mock/account";
import type { AccountModel } from "models/account";

export function load(): { accounts: AccountModel[] } {
  return {
    accounts: [...mockAccounts],
  };
}
