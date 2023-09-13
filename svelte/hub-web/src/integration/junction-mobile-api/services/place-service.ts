import { placeModel, type PlaceModel, type PlaceSchema } from "../schemas/place";
import JunctionMobileApiService from "./junction-mobile-api-service";

export class PlaceService extends JunctionMobileApiService {
  async listPlaces(query: string): Promise<PlaceModel[]> {
    const resp = await this.makeRequest<{ data: PlaceSchema[] }>("/places", {
      queryParams: { "query[name]": query },
    });

    return resp.json.data.map((item) => placeModel.toModel(item));
  }

  async getPlace(id: string): Promise<PlaceModel> {
    const resp = await this.makeRequest<{ data: PlaceSchema }>(`/places/${id}`);

    return placeModel.toModel(resp.json.data);
  }
}
