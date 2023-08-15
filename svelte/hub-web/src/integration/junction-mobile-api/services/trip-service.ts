import type { TripCandidatesModel } from "models/booking/trip";
import type { CreateTripCandidatesModel } from "../models/trip";
import {
  parseCreateTripCandidatesSearchModel,
  parseCreateTripCandidatesSearchResponseSchema,
  parseGetTripCandidatesOffersResponse,
  parseGetTripCandidatesSearchResponseSchema,
} from "../parsers/trip";
import type {
  CreateTripCandidatesSearchRequestSchema,
  CreateTripCandidatesSearchResponseSchema,
  GetTripCandidatesSearchResponseSchema,
  ListTripCandidatesOffersResponseSchema,
} from "../schemas/trip";
import JunctionMobileApiService from "./junction-mobile-api-service";
import type { OfferModel } from "models/booking/offer";

export class TripService extends JunctionMobileApiService {
  async createTripCandidatesSearch(data: CreateTripCandidatesModel): Promise<TripCandidatesModel> {
    const resp = await this.makeRequest<
      CreateTripCandidatesSearchResponseSchema,
      CreateTripCandidatesSearchRequestSchema
    >("/trip-candidates/searches", {
      method: "POST",
      data: parseCreateTripCandidatesSearchModel(data),
    });

    return parseCreateTripCandidatesSearchResponseSchema(await resp.json());
  }

  async getTripCandidatesSearch(id: string): Promise<TripCandidatesModel> {
    const resp = await this.makeRequest<GetTripCandidatesSearchResponseSchema>(
      `/trip-candidates/searches/${id}`,
    );

    if (resp.status === 404) {
      throw new Error("Trip candidates search not found");
    }

    return parseGetTripCandidatesSearchResponseSchema(await resp.json());
  }

  async getTripCandidatesOffers(id: string): Promise<OfferModel[]> {
    const resp = await this.makeRequest<ListTripCandidatesOffersResponseSchema>(
      `/trip-candidates/searches/${id}/offers`,
      {
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
      },
    );

    return parseGetTripCandidatesOffersResponse(await resp.json());
  }
}
