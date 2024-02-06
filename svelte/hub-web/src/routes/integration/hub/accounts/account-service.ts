import type AccountService from "~/integration/junction-hub-api/services/account-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<AccountService, RouteId>("/integration/hub/accounts");

export default factory({
  find: (params: { limit?: number; cursor?: string }) => [params],
  get: (params: { id: string }) => [params],
});
