import type { Session } from "integration/ory/schemas";
import JunctionMobileApiService from "./junction-mobile-api-service";
import {
  simpleOffserSearchParser,
  type SimpleOfferSearch,
  type SimpleOfferSearchCreate,
  type SimpleOfferSearchSchema,
} from "../schemas/simple-offer-search";
import type { PaginatedData } from "models/common";
import type { Offer, OfferSchema } from "../schemas/offer";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";
import {
  tripOfferSearchParser,
  type TripOfferSearch,
  type TripOfferSearchSchema,
} from "../schemas/offer-search";

export default class SimpleOfferSearchService extends JunctionMobileApiService {
  async get({ id, session }: { id: string; session: Session }): Promise<TripOfferSearch> {
    const resp = await this.makeRequest<{ data: TripOfferSearchSchema }>(`/offers/searches/${id}`, {
      session,
    });

    return tripOfferSearchParser.toModel(resp.json.data);
  }

  async create({
    session,
    data,
  }: {
    session: Session;
    data: SimpleOfferSearchCreate;
  }): Promise<SimpleOfferSearch> {
    const resp = await this.makeRequest<{ data: SimpleOfferSearchSchema }>(
      "/simple-offers/searches",
      {
        method: "POST",
        session,
        data: { data: simpleOffserSearchParser.toCreateSchema(data) },
      },
    );

    return simpleOffserSearchParser.toModel(resp.json.data);
  }

  async findOffers({
    session,
    simpleOfferSearchId,
    cursor,
    limit = 100,
    sort,
    filter,
  }: {
    session: Session;
    simpleOfferSearchId: string;
    cursor?: string;
    limit?: number;
    sort?: "createdAt" | "id";
    filter?: {
      cabinClass?: string;
    };
  }): Promise<PaginatedData<Offer>> {
    const resp = await this.makeRequest<{
      data: OfferSchema[];
      included?: IncludedSchemas;
      links: { next: string };
    }>(`/offers/searches/${simpleOfferSearchId}/offers`, {
      session,
      queryParams: {
        sort,
        "page[cursor]": cursor,
        "page[limit]": limit,
        "filter[groups.options.details.cabinClass][eq]": filter?.cabinClass,
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
    });

    const parsed = parseIncluded([...(resp.json.included ?? []), ...resp.json.data]);

    return {
      data: parsed.offers ?? [],
      cursor: SimpleOfferSearchService.getCursor(resp.json),
    };
  }
}
