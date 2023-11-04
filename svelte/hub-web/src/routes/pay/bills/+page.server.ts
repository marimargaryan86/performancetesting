import integrationInstances from "integration-instances";
import type { Bill } from "integration/junction-hub-api/schemas/bill";
import type { PaginatedData } from "models/common";
import { getSession } from "utils/auth";
import { LIST_BILLS_LIMIT } from "./+page.svelte";

export function load(event): { bills: Promise<PaginatedData<Bill>> } {
  return {
    bills: integrationInstances.junctionHubApi.bills.find({
      session: getSession(event),
      limit: LIST_BILLS_LIMIT,
    }),
  };
}
