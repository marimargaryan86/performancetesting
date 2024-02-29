import type SimpleOfferSearchService from "~/integration/junction-mobile-api/services/simple-offer-search-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import { toUtcDate } from "$lib/utils/date-time";

const factory = clientServiceFactory<SimpleOfferSearchService, RouteId>(
  "/integration/mobile/simple-offers",
);

export default factory({
  create: (params: { data: MobileSchemas.SimpleOfferSearchCreate }) => [
    {
      data: {
        ...params.data,
        criteria: {
          ...params.data.criteria,
          outbound: toUtcDate(params.data.criteria.outbound),
          inbound: params.data.criteria.inbound
            ? toUtcDate(params.data.criteria.inbound)
            : undefined,
        },
      },
    },
  ],
  get: (params: { id: string }) => [params],
  findOffers: (params: { id: string }) => [params],
});
