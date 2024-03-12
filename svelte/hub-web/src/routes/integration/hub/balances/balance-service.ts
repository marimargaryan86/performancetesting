import type BalanceService from "~/integration/junction-hub-api/services/balance-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<BalanceService, RequestEvent>("/integration/hub/balances")({
  create: (params: { accountId: string; data: HubSchemas.BalanceAdd }) => [params],
  find: (params: { accountId: string; limit?: number; cursor?: string }) => [params],
});

export { server };
export default client;
