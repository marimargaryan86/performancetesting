import JunctionMobileApiService from "./junction-mobile-api-service";
import type { Session } from "~/integration/ory/schemas/authentication";
import {
  tripCandidateSearchParser,
  type TripCandidateSearch,
  type TripCandidateSearchSchema,
  type TripCandidateSearchCreate,
} from "../schemas/trip-candidate";
import type { Offer, OfferSchema } from "../schemas/offer";
import type { PaginatedData } from "$lib/models/common";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";

export default class TripService extends JunctionMobileApiService {
  async create({
    session,
    data,
  }: {
    session: Session;
    data: TripCandidateSearchCreate;
  }): Promise<TripCandidateSearch> {
    const resp = await this.makeRequest<{ data: TripCandidateSearchSchema }>(
      "/trip-candidates/searches",
      {
        method: "POST",
        data: { data: tripCandidateSearchParser.toCreateSchema(data) },
        session,
      },
    );

    return tripCandidateSearchParser.toModel(resp.json.data);
  }

  async getTripCandidateSearch({
    session,
    id,
  }: {
    session: Session;
    id: string;
  }): Promise<TripCandidateSearch> {
    const resp = await this.makeRequest<{
      data: TripCandidateSearchSchema;
    }>(`/trip-candidates/searches/${id}`, { session });

    return tripCandidateSearchParser.toModel(resp.json.data);
  }

  async findOffers({
    session,
    id,
    cursor,
    limit = 100,
  }: {
    session: Session;
    id: string;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<Offer>> {
    const resp = await this.makeRequest<{
      data: OfferSchema[];
      included?: IncludedSchemas;
      links: { next: string };
    }>(`/trip-candidates/searches/${id}/offers`, {
      queryParams: {
        "page[cursor]": cursor,
        "page[limit]": limit,
        include: [
          "groups",
          "groups.details",
          "groups.details.legType",
          "groups.options",
          "groups.options.details",
          "groups.options.details.cabinClass",
          "groups.options.details.details",
        ].join(","),
      },
      session,
    });

    const parsed = parseIncluded([...(resp.json.included ?? []), ...resp.json.data]);

    return {
      data: parsed.offers ?? [],
      cursor: TripService.getCursor(resp.json),
    };
  }
}
