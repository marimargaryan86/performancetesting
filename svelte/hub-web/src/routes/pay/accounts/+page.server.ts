import integrationInstances from "integration-instances";
import type { AccountModel } from "integration/junction-pay/schemas/account.js";
import type { PaginatedData } from "models/common";
import { getToken } from "utils/auth";

export function load(event): { accounts: Promise<PaginatedData<AccountModel>> } {
  return {
    accounts: integrationInstances.junctionPayApi.accounts.listAccounts(getToken(event)),
  };
}

export const actions = {
  async listAccounts(event): Promise<{ accounts: PaginatedData<AccountModel> } | void> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return;
    }

    return {
      accounts: await integrationInstances.junctionPayApi.accounts.listAccounts(
        getToken(event),
        cursor,
      ),
    };
  },
};
