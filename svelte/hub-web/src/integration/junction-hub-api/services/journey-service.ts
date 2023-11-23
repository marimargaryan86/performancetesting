import type { Session } from "integration/ory/schemas/authentication";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import type { Journey, JourneySchema } from "../schemas/journey";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";

export default class JourneyService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
    sort = "id",
  }: {
    session: Session;
    cursor?: string;
    limit?: number;
    sort?: "id" | "-id" | "reference" | "-reference" | "createdAt" | "-createdAt";
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
