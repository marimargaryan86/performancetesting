import integrationInstances from "integration-instances";
import type { Account } from "integration/junction-hub-api/schemas/account";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

export function load(event): { accounts: Promise<PaginatedData<Account>> } {
  return {
    accounts: integrationInstances.junctionHubApi.accounts.listAccounts({
      session: getSession(event),
    }),
  };
}

export const actions = {
  async listAccounts(event): Promise<{ accounts: PaginatedData<Account> } | void> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return;
    }

    return {
      accounts: await integrationInstances.junctionHubApi.accounts.listAccounts({
        session: getSession(event),
        cursor,
      }),
    };
  },
};
