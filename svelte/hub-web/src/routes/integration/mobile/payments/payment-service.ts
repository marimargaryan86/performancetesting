import type PaymentService from "~/integration/junction-mobile-api/services/payment-service";
import type * as CommonSchemas from "~/integration/common/schemas";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<PaymentService, RequestEvent>("/integration/mobile/payments")({
  create: (params: { data: CommonSchemas.Price }) => [params],
});

export { server };
export default client;
