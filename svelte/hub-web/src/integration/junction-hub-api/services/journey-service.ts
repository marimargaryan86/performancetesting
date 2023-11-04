import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import type { Journey, JourneySchema } from "../schemas/journey";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";

export default class JourneyService extends JunctionHubApiService {
  async listJourneys({
    session,
    cursor,
    limit = 100,
  }: {
    session: SessionModel;
    cursor?: string;
    limit?: number;
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
        include: ["orders", "orders.bookings", "orders.bookings.details"].join(","),
      },
    });

    const parsed = parseIncluded([...(resp.json.included ?? []), ...resp.json.data]);

    return {
      data: parsed.journeys ?? [],
      cursor: JourneyService.getCursor(resp.json),
    };
  }
}
