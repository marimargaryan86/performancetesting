import type BalanceService from "~/integration/junction-hub-api/services/balance-service";
import { clientServiceFactory } from "../../framework";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<BalanceService, RouteId>("/integration/hub/balances");

export default factory({
  create: (params: { accountId: string; data: HubSchemas.BalanceAdd }) => [params],
  find: (params: { accountId: string; limit?: number; cursor?: string }) => [params],
});
