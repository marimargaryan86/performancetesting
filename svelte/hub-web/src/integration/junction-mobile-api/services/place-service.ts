import type { SessionModel } from "models/user";
import { placeModel, type PlaceModel, type PlaceSchema } from "../schemas/place";
import JunctionMobileApiService from "./junction-mobile-api-service";

export class PlaceService extends JunctionMobileApiService {
  async listPlaces({
    session,
    query,
  }: {
    session: SessionModel;
    query: string;
  }): Promise<PlaceModel[]> {
    const resp = await this.makeRequest<{ data: PlaceSchema[] }>("/places", {
      queryParams: { "query[name]": query },
      session,
    });

    return resp.json.data.map((item) => placeModel.toModel(item));
  }

  async getPlace({ session, id }: { session: SessionModel; id: string }): Promise<PlaceModel> {
    const resp = await this.makeRequest<{ data: PlaceSchema }>(`/places/${id}`, { session });

    return placeModel.toModel(resp.json.data);
  }
}
