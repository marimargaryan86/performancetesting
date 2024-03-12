import type SimpleOfferSearchService from "~/integration/junction-mobile-api/services/simple-offer-search-service";
import type { RequestEvent } from "./$types";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<SimpleOfferSearchService, RequestEvent>(
  "/integration/mobile/simple-offers",
)({
  create: (params: { data: MobileSchemas.SimpleOfferSearchCreate }) => [params],
  get: (params: { id: string }) => [params],
  findOffers: (params: { id: string }) => [params],
});

export { server };
export default client;
