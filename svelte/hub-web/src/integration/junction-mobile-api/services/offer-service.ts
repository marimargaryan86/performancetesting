import type { OfferPriceQuoteModel } from "models/booking/offer";
import { parsePriceQuoteSchema } from "../parsers/offer";
import type {
  CreateOfferPriceQuoteResponseSchema,
  CreateOfferPriceQuoteRequestSchema,
  GetOfferPriceQuoteResponseSchema,
} from "../schemas/offer";
import JunctionMobileApiService from "./junction-mobile-api-service";

export class OfferService extends JunctionMobileApiService {
  async createPriceQuote(data: {
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
    });

    const respData = await resp.json();

    return parsePriceQuoteSchema(respData.data);
  }

  async getPriceQuote(id: string): Promise<OfferPriceQuoteModel> {
    const resp = await this.makeRequest<GetOfferPriceQuoteResponseSchema>(`/offers/quotes/${id}`);

    if (resp.status === 404) {
      throw new Error("Quote not found");
    }

    const respData = await resp.json();

    return parsePriceQuoteSchema(respData.data);
  }
}
