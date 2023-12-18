import type JourneyService from "integration/junction-hub-api/services/journey-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<JourneyService, RouteId>("/integration/hub/journeys");

export default factory<{
  find: [
    params: {
      cursor?: string;
      limit?: number;
      sort?: Parameters<JourneyService["find"]>[0]["sort"];
    },
  ];
}>({
  find: true,
});
