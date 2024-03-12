import type RefundService from "~/integration/junction-hub-api/services/refund-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<RefundService, RequestEvent>("/integration/hub/refunds")({
  find: (params: { cursor?: string; limit?: number }) => [params],
  get: (params: { id: string }) => [params],
  getRefundPosition: (params: { refundId: string; data: HubSchemas.RefundPositionCreate }) => [
    params,
  ],
  update: (params: { id: string; data: HubSchemas.RefundPut }) => [params],
});

export { server };
export default client;
