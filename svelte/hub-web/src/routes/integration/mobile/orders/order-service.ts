import type OrderService from "integration/junction-mobile-api/services/order-service";
import type { OrderCreate } from "integration/junction-mobile-api/schemas/order";
import type { MarkupsCreate } from "integration/junction-mobile-api/schemas/markups";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<OrderService, RouteId>("/integration/mobile/orders");

export default factory({
  create: (params: { data: OrderCreate }) => [params],
  createMarkups: (params: { data: MarkupsCreate }) => [params],
  find: (params: { cursor?: string; limit?: number }) => [params],
  get: (params: { id: string }) => [params],
  getMarkups: (params: { orderId: string }) => [params],
});
