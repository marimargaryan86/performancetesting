import type ConversionService from "~/integration/junction-hub-api/services/conversion-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<ConversionService, RequestEvent>("/integration/hub/conversions")(
  {
    find: (params: { cursor?: string; limit?: number }) => [params],
    get: (params: { id: string }) => [params],
  },
);

export { server };
export default client;
