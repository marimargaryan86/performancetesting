import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type OfferService from "~/integration/junction-mobile-api/services/offer-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<OfferService, RequestEvent>("/integration/mobile/offers")({
  create: (params: { data: MobileSchemas.TripOfferPriceQuoteCreate }) => [params],
  get: (params: { id: string }) => [params],
});

export { server };
export default client;
