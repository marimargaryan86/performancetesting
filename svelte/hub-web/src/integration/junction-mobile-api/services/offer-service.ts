import JunctionMobileApiService from "./junction-mobile-api-service";
import type { Session } from "integration/ory/schemas/authentication";
import {
  tripOfferPriceQuoteParser,
  type TripOfferPriceQuoteCreate,
  type TripOfferPriceQuote,
  type TripOfferPriceQuoteSchema,
} from "../schemas/trip-offer-price-quote";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";
import { JunctionError } from "integration/common/junction-error";

export default class OfferService extends JunctionMobileApiService {
  async create({
    session,
    data,
  }: {
    session: Session;
    data: TripOfferPriceQuoteCreate;
  }): Promise<TripOfferPriceQuote> {
    const resp = await this.makeRequest<{ data: TripOfferPriceQuoteSchema }>("/offers/quotes", {
      method: "POST",
      data: {
        data: tripOfferPriceQuoteParser.toCreateSchema(data),
      },
      session,
    });

    return tripOfferPriceQuoteParser.toModel(resp.json.data);
  }

  async get({ id, session }: { session: Session; id: string }): Promise<TripOfferPriceQuote> {
    const resp = await this.makeRequest<{
      data: TripOfferPriceQuoteSchema;
      included?: IncludedSchemas;
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

    const parsed = parseIncluded([...(resp.json.included ?? []), resp.json.data]);
    const priceQuote = parsed.tripOfferPriceQuotes?.find((item) => item.id === id);

    if (!priceQuote) {
      throw new JunctionError({ status: 404, statusText: "Not found" });
    }

    return priceQuote;
  }
}
