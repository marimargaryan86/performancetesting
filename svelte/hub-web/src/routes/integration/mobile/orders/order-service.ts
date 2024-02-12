import type OrderService from "~/integration/junction-mobile-api/services/order-service";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<OrderService, RouteId>("/integration/mobile/orders");

export default factory({
  create: (params: { data: MobileSchemas.OrderCreate }) => [params],
  createMarkups: (params: { data: MobileSchemas.MarkupsCreate }) => [params],
  find: (params: { cursor?: string; limit?: number }) => [params],
  get: (params: { id: string }) => [params],
  getMarkups: (params: { orderId: string }) => [params],
});
