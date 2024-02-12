import type RefundService from "~/integration/junction-hub-api/services/refund-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<RefundService, RouteId>("/integration/hub/refunds");

export default factory({
  find: (params: { cursor?: string; limit?: number }) => [params],
  get: (params: { id: string }) => [params],
  getRefundPosition: (params: { refundId: string; data: HubSchemas.RefundPositionCreate }) => [
    params,
  ],
  update: (params: { id: string; data: HubSchemas.RefundPut }) => [params],
});
