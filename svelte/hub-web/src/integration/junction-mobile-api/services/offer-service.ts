import { parsePriceQuoteSchema } from "../parsers/offer";
import {
  createTripOfferPriceQuoteModel,
  type CreateTripOfferPriceQuoteModel,
  type TripOfferPriceQuoteIncludes,
  type TripOfferPriceQuoteModel,
  type TripOfferPriceQuoteSchema,
} from "../schemas/offer";
import JunctionMobileApiService from "./junction-mobile-api-service";
import { parseIncluded } from "../parsers/included";
import type { SessionModel } from "models/user";

export class OfferService extends JunctionMobileApiService {
  async createPriceQuote({
    session,
    data,
  }: {
    session: SessionModel;
    data: CreateTripOfferPriceQuoteModel;
  }): Promise<TripOfferPriceQuoteModel> {
    const resp = await this.makeRequest<{ data: TripOfferPriceQuoteSchema }>("/offers/quotes", {
      method: "POST",
      data: {
        data: createTripOfferPriceQuoteModel.toSchema(data),
      },
      headers: { "Session-Token": data.sessionToken },
      session,
    });

    return parsePriceQuoteSchema(resp.json.data);
  }

  async getPriceQuote({
    id,
    session,
  }: {
    session: SessionModel;
    id: string;
  }): Promise<TripOfferPriceQuoteModel> {
    const resp = await this.makeRequest<{
      data: TripOfferPriceQuoteSchema;
      included?: TripOfferPriceQuoteIncludes[];
    }>(`/offers/quotes/${id}`, {
      queryParams: {
        include: [
          "offer",
          "offer.groups",
          "offer.groups.details",
          "offer.groups.details.legType",
          "options",
          "options.details",
          "options.details.cabinClass",
          "options.details.details",
        ].join(","),
      },
      session,
    });

    const included = parseIncluded(resp.json.included);

    return parsePriceQuoteSchema(resp.json.data, included);
  }
}
