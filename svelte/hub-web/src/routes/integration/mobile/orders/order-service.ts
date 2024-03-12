import type OrderService from "~/integration/junction-mobile-api/services/order-service";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<OrderService, RequestEvent>("/integration/mobile/orders")({
  create: (params: { data: MobileSchemas.OrderCreate }) => [params],
  createMarkups: (params: { data: MobileSchemas.MarkupsCreate }) => [params],
  find: (params: { cursor?: string; limit?: number }) => [params],
  get: (params: { id: string }) => [params],
  getMarkups: (params: { orderId: string }) => [params],
});

export { server };
export default client;
