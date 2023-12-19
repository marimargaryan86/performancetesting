import type PlaceService from "integration/junction-mobile-api/services/place-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<PlaceService, RouteId>("/integration/mobile/places");

export default factory({
  find: (query: string) => [query],
  get: (params: { id: string }) => [params],
});
