import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type OfferService from "~/integration/junction-mobile-api/services/offer-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<OfferService, RouteId>("/integration/mobile/offers");

export default factory({
  create: (params: { data: MobileSchemas.TripOfferPriceQuoteCreate }) => [params],
  get: (params: { id: string }) => [params],
});
