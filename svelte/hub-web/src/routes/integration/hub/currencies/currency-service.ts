import type CurrencyService from "~/integration/junction-hub-api/services/currency-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<CurrencyService, RequestEvent>("/integration/hub/currencies")({
  find: (params: { cursor?: string; limit?: number }) => [params],
});

export { server };
export default client;
