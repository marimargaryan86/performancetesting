import type PaymentService from "integration/junction-mobile-api/services/payment-service";
import type { Price } from "integration/common/schemas/price";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<PaymentService, RouteId>("/integration/mobile/payments");

export default factory<{
  create: [params: { data: Price }];
}>({
  create: true,
});
