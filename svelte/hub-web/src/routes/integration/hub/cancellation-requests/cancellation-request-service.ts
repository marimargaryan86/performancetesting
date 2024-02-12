import type CancellationRequestService from "~/integration/junction-hub-api/services/cancellation-request-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<CancellationRequestService, RouteId>(
  "/integration/hub/cancellation-requests",
);

export default factory({
  create: (params: { data: HubSchemas.CancellationRequestCreate }) => [params],
});
