import type { CancellationRequestCreate } from "integration/junction-mobile-api/schemas/cancellation";
import type CancellationRequestService from "integration/junction-mobile-api/services/cancellation-request-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<CancellationRequestService, RouteId>(
  "/integration/mobile/cancellation-requests",
);

export default factory({
  create: (params: { data: CancellationRequestCreate }) => [params],
  get: (params: { id: string }) => [params],
});
