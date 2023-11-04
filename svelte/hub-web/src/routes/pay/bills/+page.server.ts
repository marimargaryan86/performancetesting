import integrationInstances from "integration-instances";
import type { Bill } from "integration/junction-hub-api/schemas/bill";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

const LIST_BILLS_LIMIT = 20;

export function load(event): { bills: Promise<PaginatedData<Bill>> } {
  return {
    bills: integrationInstances.junctionHubApi.bills.listBills({
      session: getSession(event),
      limit: LIST_BILLS_LIMIT,
    }),
  };
}

export const actions = {
  async listBills(event): Promise<{ bills: PaginatedData<Bill> }> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return {
        bills: { data: [] },
      };
    }

    return {
      bills: await integrationInstances.junctionHubApi.bills.listBills({
        session: getSession(event),
        limit: LIST_BILLS_LIMIT,
        cursor,
      }),
    };
  },
  async toggleReconciliation(event): Promise<void> {
    const session = getSession(event);
    const formData = await event.request.formData();
    const billId = formData.get("billId")?.toString();

    if (!billId) {
      return;
    }

    try {
      await integrationInstances.junctionHubApi.bills.toggleReconciliation({
        session,
        bill: await integrationInstances.junctionHubApi.bills.getBill({
          session,
          billId,
        }),
      });
    } catch {
      return;
    }
  },
};
