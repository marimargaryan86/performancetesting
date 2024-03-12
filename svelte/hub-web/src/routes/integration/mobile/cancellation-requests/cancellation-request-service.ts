import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type CancellationRequestService from "~/integration/junction-mobile-api/services/cancellation-request-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<CancellationRequestService, RequestEvent>(
  "/integration/mobile/cancellation-requests",
)({
  create: (params: { data: MobileSchemas.CancellationRequestCreate }) => [params],
  get: (params: { id: string }) => [params],
});

export { server };
export default client;
