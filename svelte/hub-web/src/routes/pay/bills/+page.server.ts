import integrationInstances from "integration-instances";
import type { BillModel } from "integration/junction-hub-api/schemas/bill";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";

export function load(event): { bills: Promise<PaginatedData<BillModel>> } {
  return {
    bills: integrationInstances.junctionPayApi.bills.listBills({
      session: getSession(event),
    }),
  };
}

export const actions = {
  async listBills(event): Promise<{ bills: PaginatedData<BillModel> }> {
    const formData = await event.request.formData();
    const cursor = formData.get("cursor")?.toString();

    if (!cursor) {
      return {
        bills: { data: [] },
      };
    }

    return {
      bills: await integrationInstances.junctionPayApi.bills.listBills({
        session: getSession(event),
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
      await integrationInstances.junctionPayApi.bills.toggleReconciliation({
        session,
        bill: await integrationInstances.junctionPayApi.bills.getBill({
          session,
          billId,
        }),
      });
    } catch {
      return;
    }
  },
};
