import type { TripOfferPriceQuoteCreate } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
import type OfferService from "integration/junction-mobile-api/services/offer-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<OfferService, RouteId>("/integration/mobile/offers");

export default factory({
  create: (params: { data: TripOfferPriceQuoteCreate }) => [params],
  get: (params: { id: string }) => [params],
});
