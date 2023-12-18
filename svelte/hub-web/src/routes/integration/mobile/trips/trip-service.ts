import type TripService from "integration/junction-mobile-api/services/trip-service";
import type { TripCandidateSearchCreate } from "integration/junction-mobile-api/schemas/trip-candidate";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<TripService, RouteId>("/integration/mobile/trips");

export default factory<{
  create: [params: { data: TripCandidateSearchCreate }];
  findOffers: [params: { id: string; cursor?: string; limit?: number }];
  getTripCandidateSearch: [params: { id: string }];
}>({
  create: true,
  findOffers: true,
  getTripCandidateSearch: true,
});
