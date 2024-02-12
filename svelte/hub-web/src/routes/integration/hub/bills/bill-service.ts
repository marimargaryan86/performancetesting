import { clientServiceFactory } from "../../framework";
import type BillService from "~/integration/junction-hub-api/services/bill-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<BillService, RouteId>("/integration/hub/bills");

export default factory({
  find: (params: {
    limit?: number;
    cursor?: string;
    filter?: Parameters<BillService["find"]>[0]["filter"];
  }) => [params],
  get: (params: { id: string }) => [params],
  toggleReconciliation: (params: { bill: HubSchemas.Bill }) => [params],
});
