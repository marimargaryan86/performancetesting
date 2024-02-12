import type * as OrySchemas from "~/integration/ory/schemas";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "$lib/models/common";
import * as Schemas from "../schemas";

export default class JourneyService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
    sort = "id",
    filter,
  }: {
    session: OrySchemas.Session;
    cursor?: string;
    limit?: number;
    sort?: "id" | "-id" | "reference" | "-reference" | "createdAt" | "-createdAt";
    filter?: Schemas.JourneyFilterOptions;
  }): Promise<PaginatedData<Schemas.Journey>> {
    const resp = await this.makeRequest<{
      data: Schemas.JourneySchema[];
      included?: Schemas.IncludedSchemas;
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

    const parsed = Schemas.parseIncluded([...(resp.json.included ?? []), ...resp.json.data]);

    return {
      data: parsed.journeys ?? [],
      cursor: JourneyService.getCursor(resp.json),
    };
  }
}
