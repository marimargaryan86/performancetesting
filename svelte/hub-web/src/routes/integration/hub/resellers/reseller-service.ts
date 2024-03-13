import type ResellerService from "~/integration/junction-hub-api/services/reseller-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<ResellerService, RequestEvent>("/integration/hub/resellers")({
  find: (params: { cursor?: string; limit?: number }) => [params],
});

export { server };
export default client;
