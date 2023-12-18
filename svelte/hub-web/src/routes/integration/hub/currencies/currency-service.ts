import type CurrencyService from "integration/junction-hub-api/services/currency-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<CurrencyService, RouteId>("/integration/hub/currencies");

export default factory<{
  find: [params: { cursor?: string; limit?: number }];
}>({
  find: true,
});
