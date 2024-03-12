import type BillService from "~/integration/junction-hub-api/services/bill-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<BillService, RequestEvent>("/integration/hub/bills")({
  find: (params: {
    limit?: number;
    cursor?: string;
    filter?: Parameters<BillService["find"]>[0]["filter"];
  }) => [params],
  get: (params: { id: string }) => [params],
  toggleReconciliation: (params: { bill: HubSchemas.Bill }) => [params],
});

export { server };
export default client;
