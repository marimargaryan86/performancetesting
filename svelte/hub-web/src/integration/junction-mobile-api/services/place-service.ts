import type { PlaceModel } from "models/booking/location";
import type { GetPlaceResponseSchema, ListPlacesResponseSchema } from "../schemas/place";
import JunctionMobileApiService from "./junction-mobile-api-service";
import { parsePlaceSchema } from "../parsers/place";

export class PlaceService extends JunctionMobileApiService {
  async listPlaces(query: string): Promise<PlaceModel[]> {
    const resp = await this.makeRequest<ListPlacesResponseSchema>("/places", {
      queryParams: { "query[name]": query },
    });

    return (await resp.json()).data.map(parsePlaceSchema);
  }

  async getPlace(id: string): Promise<PlaceModel> {
    const resp = await this.makeRequest<GetPlaceResponseSchema>(`/places/${id}`);

    if (resp.status === 404) {
      throw new Error("Place not found");
    }

    return parsePlaceSchema((await resp.json()).data);
  }
}
