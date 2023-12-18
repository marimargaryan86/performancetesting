import type OrderService from "integration/junction-mobile-api/services/order-service";
import type { OrderCreate } from "integration/junction-mobile-api/schemas/order";
import type { MarkupsCreate } from "integration/junction-mobile-api/schemas/markups";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<OrderService, RouteId>("/integration/mobile/orders");

export default factory<{
  create: [params: { data: OrderCreate }];
  find: [params: { cursor?: string; limit?: number }];
  get: [params: { id: string }];
  getMarkups: [params: { orderId: string }];
  createMarkups: [params: { data: MarkupsCreate }];
}>({
  create: true,
  createMarkups: true,
  find: true,
  get: true,
  getMarkups: true,
});
