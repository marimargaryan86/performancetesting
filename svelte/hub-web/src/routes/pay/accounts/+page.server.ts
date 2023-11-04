import integrationInstances from "integration-instances";
import type { Account } from "integration/junction-hub-api/schemas/account";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

const LIST_ACCOUNTS_LIMIT = 20;

export function load(event): { accounts: Promise<PaginatedData<Account>> } {
  return {
    accounts: integrationInstances.junctionHubApi.accounts.listAccounts({
      session: getSession(event),
      limit: LIST_ACCOUNTS_LIMIT,
    }),
  };
}

export const actions = {
  async listAccounts(event): Promise<{ accounts: PaginatedData<Account> }> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return { accounts: { data: [] } };
    }

    return {
      accounts: await integrationInstances.junctionHubApi.accounts.listAccounts({
        session: getSession(event),
        limit: LIST_ACCOUNTS_LIMIT,
        cursor,
      }),
    };
  },
};
