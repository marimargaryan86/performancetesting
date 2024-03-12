import type CancellationRequestService from "~/integration/junction-hub-api/services/cancellation-request-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<CancellationRequestService, RequestEvent>(
  "/integration/hub/cancellation-requests",
)({
  create: (params: { data: HubSchemas.CancellationRequestCreate }) => [params],
});

export { server };
export default client;
