import type PaymentService from "~/integration/junction-mobile-api/services/payment-service";
import type * as CommonSchemas from "~/integration/common/schemas";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<PaymentService, RouteId>("/integration/mobile/payments");

export default factory({
  create: (params: { data: CommonSchemas.Price }) => [params],
});
