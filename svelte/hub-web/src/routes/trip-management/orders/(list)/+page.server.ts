import integrationInstances from "integration-instances";
import type { Journey, JourneyFilterOptions } from "integration/junction-hub-api/schemas/journey";
import type { PaginatedData } from "models/common";
import { LIST_JOURNEYS_LIMIT, LIST_JOURNEYS_SORT } from "./+page.svelte";
import { bookingStatuses } from "integration/junction-hub-api/schemas/booking";
import { parseDateRange } from "utils/date-time";

export function load(event): { journeys: Promise<PaginatedData<Journey>> } {
  const { searchParams } = event.url;
  const filter: JourneyFilterOptions = {
    createdAtRange: parseDateRange(
      searchParams.get("createdAt[from]") ?? undefined,
      searchParams.get("createdAt[to]") ?? undefined,
    ),
    departureAtRange: parseDateRange(
      searchParams.get("departureAt[from]") ?? undefined,
      searchParams.get("departureAt[to]") ?? undefined,
    ),
    bookingStatus: bookingStatuses.find((status) => searchParams.get("bookingStatus") === status),
  };

  return {
    journeys: integrationInstances.junctionHubApi.journeys.find({
      limit: LIST_JOURNEYS_LIMIT,
      session: event.locals.session,
      sort: LIST_JOURNEYS_SORT,
      filter,
    }),
  };
}
