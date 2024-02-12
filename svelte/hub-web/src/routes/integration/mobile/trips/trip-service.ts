import type TripService from "~/integration/junction-mobile-api/services/trip-service";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<TripService, RouteId>("/integration/mobile/trips");

export default factory({
  create: (params: { data: MobileSchemas.TripCandidateSearchCreate }) => [params],
  findOffers: (params: { id: string; cursor?: string; limit?: number }) => [params],
  getTripCandidateSearch: (params: { id: string }) => [params],
});
