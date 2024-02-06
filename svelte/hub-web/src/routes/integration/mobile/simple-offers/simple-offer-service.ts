import type SimpleOfferSearchService from "~/integration/junction-mobile-api/services/simple-offer-search-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";
import type { SimpleOfferSearchCreate } from "~/integration/junction-mobile-api/schemas/simple-offer-search";

const factory = clientServiceFactory<SimpleOfferSearchService, RouteId>(
  "/integration/mobile/simple-offers",
);

export default factory({
  create: (params: { data: SimpleOfferSearchCreate }) => [params],
  get: (params: { id: string }) => [params],
  findOffers: (params: { id: string }) => [params],
});
