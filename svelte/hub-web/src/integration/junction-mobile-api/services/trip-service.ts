import { tripCandidatesSearchModel, createTripCandidatesSearchModel } from "../schemas/trip";
import JunctionMobileApiService from "./junction-mobile-api-service";
import type { Infer } from "../schema-model.server";
import type { OfferIncludes, offerModel } from "../schemas/offer";
import { parseOfferSchema } from "../parsers/offer";
import { parseIncluded } from "../parsers/included";

export class TripService extends JunctionMobileApiService {
  async createTripCandidatesSearch(
    data: Infer<typeof createTripCandidatesSearchModel>,
  ): Promise<Infer<typeof tripCandidatesSearchModel>> {
    const resp = await this.makeRequest<
      { data: Infer<typeof tripCandidatesSearchModel, "schema"> },
      { data: Infer<typeof createTripCandidatesSearchModel, "schema"> }
    >("/trip-candidates/searches", {
      method: "POST",
      data: { data: createTripCandidatesSearchModel.toSchema(data) },
    });

    return tripCandidatesSearchModel.toModel((await resp.json()).data);
  }

  async getTripCandidatesSearch(id: string): Promise<Infer<typeof tripCandidatesSearchModel>> {
    const resp = await this.makeRequest<{
      data: Infer<typeof tripCandidatesSearchModel, "schema">;
    }>(`/trip-candidates/searches/${id}`);

    if (resp.status === 404) {
      throw new Error("Trip candidates search not found");
    }

    return tripCandidatesSearchModel.toModel((await resp.json()).data);
  }

  async getTripCandidatesOffers(id: string): Promise<Infer<typeof offerModel>[]> {
    const resp = await this.makeRequest<{
      data: Infer<typeof offerModel, "schema">[];
      included?: OfferIncludes;
    }>(`/trip-candidates/searches/${id}/offers`, {
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

    const data = await resp.json();
    const included = parseIncluded(data.included);

    return data.data.map((item) => parseOfferSchema(item, included));
  }
}
