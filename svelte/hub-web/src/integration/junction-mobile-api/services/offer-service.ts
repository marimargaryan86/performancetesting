import type { OfferPriceQuoteModel } from "models/booking/offer";
import { parseGetPriceQuoteSchema, parsePriceQuoteSchema } from "../parsers/offer";
import type {
  CreateOfferPriceQuoteResponseSchema,
  CreateOfferPriceQuoteRequestSchema,
  GetOfferPriceQuoteResponseSchema,
} from "../schemas/offer";
import JunctionMobileApiService from "./junction-mobile-api-service";

export class OfferService extends JunctionMobileApiService {
  async createPriceQuote(data: {
    sessionToken: string;
    offerId: string;
    optionIds: string[];
  }): Promise<OfferPriceQuoteModel> {
    const resp = await this.makeRequest<
      CreateOfferPriceQuoteResponseSchema,
      CreateOfferPriceQuoteRequestSchema
    >("/offers/quotes", {
      method: "POST",
      data: {
        data: {
          type: "trip-offer-price-quotes",
          relationships: {
            offer: { data: { id: data.offerId, type: "offers" } },
            options: {
              data: data.optionIds.map((id) => ({ id, type: "offer-options" })),
            },
          },
        },
      },
      headers: { "Session-Token": data.sessionToken },
    });

    const respData = await resp.json();

    return parsePriceQuoteSchema(respData.data);
  }

  async getPriceQuote(id: string): Promise<OfferPriceQuoteModel> {
    const resp = await this.makeRequest<GetOfferPriceQuoteResponseSchema>(`/offers/quotes/${id}`, {
      queryParams: {
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

    if (resp.status === 404) {
      throw new Error("Quote not found");
    }

    return parseGetPriceQuoteSchema(await resp.json());
  }
}
