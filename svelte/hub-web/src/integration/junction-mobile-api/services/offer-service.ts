import { parsePriceQuoteSchema } from "../parsers/offer";
import {
  createTripOfferPriceQuoteModel,
  tripOfferPriceQuoteModel,
  type TripOfferPriceQuoteIncludes,
} from "../schemas/offer";
import JunctionMobileApiService from "./junction-mobile-api-service";
import type { Infer } from "../schema-model.server";
import { parseIncluded } from "../parsers/included";

export class OfferService extends JunctionMobileApiService {
  async createPriceQuote(
    data: Infer<typeof createTripOfferPriceQuoteModel>,
  ): Promise<Infer<typeof tripOfferPriceQuoteModel>> {
    const resp = await this.makeRequest<
      { data: Infer<typeof tripOfferPriceQuoteModel, "schema"> },
      { data: Infer<typeof createTripOfferPriceQuoteModel, "schema"> }
    >("/offers/quotes", {
      method: "POST",
      data: {
        data: createTripOfferPriceQuoteModel.toSchema(data),
      },
      headers: { "Session-Token": data.sessionToken },
    });

    const respData = await resp.json();

    return parsePriceQuoteSchema(respData.data, { offers: [] });
  }

  async getPriceQuote(id: string): Promise<Infer<typeof tripOfferPriceQuoteModel>> {
    const resp = await this.makeRequest<{
      data: Infer<typeof tripOfferPriceQuoteModel, "schema">;
      included?: TripOfferPriceQuoteIncludes;
    }>(`/offers/quotes/${id}`, {
      queryParams: {
        include: ["offers", "options"].join(","),
      },
    });

    if (resp.status === 404) {
      throw new Error("Quote not found");
    }

    const data = await resp.json();
    const included = parseIncluded(data.included);

    return parsePriceQuoteSchema(data.data, included);
  }
}
