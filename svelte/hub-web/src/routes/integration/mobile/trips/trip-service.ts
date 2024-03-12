import type TripService from "~/integration/junction-mobile-api/services/trip-service";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<TripService, RequestEvent>("/integration/mobile/trips")({
  create: (params: { data: MobileSchemas.TripCandidateSearchCreate }) => [params],
  findOffers: (params: { id: string; cursor?: string; limit?: number }) => [params],
  getTripCandidateSearch: (params: { id: string }) => [params],
});

export { server };
export default client;
