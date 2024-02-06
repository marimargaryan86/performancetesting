import type ConversionService from "~/integration/junction-hub-api/services/conversion-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<ConversionService, RouteId>("/integration/hub/conversions");

export default factory({
  find: (params: { cursor?: string; limit?: number }) => [params],
  get: (params: { id: string }) => [params],
});
