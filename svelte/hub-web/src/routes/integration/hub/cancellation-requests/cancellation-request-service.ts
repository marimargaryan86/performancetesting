import type { CancellationRequestCreate } from "integration/junction-hub-api/schemas/cancellation";
import type CancellationRequestService from "integration/junction-hub-api/services/cancellation-request-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<CancellationRequestService, RouteId>(
  "/integration/hub/cancellation-requests",
);

export default factory<{ create: [params: { data: CancellationRequestCreate }] }>({
  create: true,
});
