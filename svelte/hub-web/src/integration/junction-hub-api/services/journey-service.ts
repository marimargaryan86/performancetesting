import type { Session } from "integration/ory/schemas/authentication";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import type { Journey, JourneySchema } from "../schemas/journey";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";
import type { JourneyFilterOptions } from "integration/junction-hub-api/schemas/journey";

export default class JourneyService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
    sort = "id",
    filter,
  }: {
    session: Session;
    cursor?: string;
    limit?: number;
    sort?: "id" | "-id" | "reference" | "-reference" | "createdAt" | "-createdAt";
    filter?: JourneyFilterOptions;
  }): Promise<PaginatedData<Journey>> {
    const resp = await this.makeRequest<{
      data: JourneySchema[];
      included?: IncludedSchemas;
      links: { next: string };
    }>("/journeys", {
      session,
      queryParams: {
        "page[cursor]": cursor,
        "page[limit]": limit,
        "filter[createdAt][ge]": filter?.createdAtRange?.from.toISOString(),
        "filter[createdAt][le]": filter?.createdAtRange?.to.toISOString(),
        "filter[departureDate][ge]": filter?.departureAtRange?.from.toISOString(),
        "filter[departureDate][le]": filter?.departureAtRange?.to.toISOString(),
        "filter[status][eq]": filter?.bookingStatus,
        "filter[passengerLastName][like]": filter?.passengerLastName,
        "filter[pnr][eq]": filter?.passengerNameRecord,
        sort,
        include: [
          "orders",
          "orders.bookings",
          "orders.bookings.details",
          "orders.bookings.bookingCancellation",
          "orders.bookings.transaction",
          "orders.bookings.refund",
        ].join(","),
      },
    });

    const parsed = parseIncluded([...(resp.json.included ?? []), ...resp.json.data]);

    return {
      data: parsed.journeys ?? [],
      cursor: JourneyService.getCursor(resp.json),
    };
  }
}
