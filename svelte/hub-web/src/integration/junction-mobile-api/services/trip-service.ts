import {
  tripCandidatesSearchModel,
  createTripCandidatesSearchModel,
  type TripCandidatesSearchModel,
  type TripCandidatesSearchSchema,
  type CreateTripCandidatesSearchModel,
} from "../schemas/trip";
import JunctionMobileApiService from "./junction-mobile-api-service";
import type { OfferIncludes, OfferModel, OfferSchema } from "../schemas/offer";
import { parseOfferSchema } from "../parsers/offer";
import { parseIncluded } from "../parsers/included";

export class TripService extends JunctionMobileApiService {
  async createTripCandidatesSearch(
    data: CreateTripCandidatesSearchModel,
  ): Promise<TripCandidatesSearchModel> {
    const resp = await this.makeRequest<{ data: TripCandidatesSearchSchema }>(
      "/trip-candidates/searches",
      {
        method: "POST",
        data: { data: createTripCandidatesSearchModel.toSchema(data) },
      },
    );

    return tripCandidatesSearchModel.toModel(resp.json.data);
  }

  async getTripCandidatesSearch(id: string): Promise<TripCandidatesSearchModel> {
    const resp = await this.makeRequest<{
      data: TripCandidatesSearchSchema;
    }>(`/trip-candidates/searches/${id}`);

    return tripCandidatesSearchModel.toModel(resp.json.data);
  }

  async getTripCandidatesOffers(id: string): Promise<OfferModel[]> {
    const resp = await this.makeRequest<{
      data: OfferSchema[];
      included?: OfferIncludes[];
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

    const included = parseIncluded(resp.json.included);

    return resp.json.data.map((item) => parseOfferSchema(item, included));
  }
}
