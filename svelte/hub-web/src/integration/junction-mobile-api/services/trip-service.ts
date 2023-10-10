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
import type { SessionModel } from "models/user";

export class TripService extends JunctionMobileApiService {
  async createTripCandidatesSearch({
    session,
    data,
  }: {
    session: SessionModel;
    data: CreateTripCandidatesSearchModel;
  }): Promise<TripCandidatesSearchModel> {
    const resp = await this.makeRequest<{ data: TripCandidatesSearchSchema }>(
      "/trip-candidates/searches",
      {
        method: "POST",
        data: { data: createTripCandidatesSearchModel.toSchema(data) },
        session,
      },
    );

    return tripCandidatesSearchModel.toModel(resp.json.data);
  }

  async getTripCandidatesSearch({
    session,
    id,
  }: {
    session: SessionModel;
    id: string;
  }): Promise<TripCandidatesSearchModel> {
    const resp = await this.makeRequest<{
      data: TripCandidatesSearchSchema;
    }>(`/trip-candidates/searches/${id}`, { session });

    return tripCandidatesSearchModel.toModel(resp.json.data);
  }

  async getTripCandidatesOffers({
    session,
    id,
  }: {
    session: SessionModel;
    id: string;
  }): Promise<OfferModel[]> {
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
      session,
    });

    const included = parseIncluded(resp.json.included);

    return resp.json.data.map((item) => parseOfferSchema(item, included));
  }
}
