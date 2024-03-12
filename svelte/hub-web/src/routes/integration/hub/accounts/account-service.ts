import type AccountService from "~/integration/junction-hub-api/services/account-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<AccountService, RequestEvent>("/integration/hub/accounts")({
  find: (params: { limit?: number; cursor?: string }) => [params],
  get: (params: { id: string }) => [params],
});

export { server };
export default client;
