import { clientServiceFactory } from "../../framework";
import type BillService from "integration/junction-hub-api/services/bill-service";
import type { Bill } from "integration/junction-hub-api/schemas/bill";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<BillService, RouteId>("/integration/hub/bills");

export default factory<{
  find: [
    params: {
      limit?: number;
      cursor?: string;
      filter?: Parameters<BillService["find"]>[0]["filter"];
    },
  ];
  get: [params: { id: string }];
  toggleReconciliation: [params: { bill: Bill }];
}>({
  find: true,
  get: true,
  toggleReconciliation: true,
});
