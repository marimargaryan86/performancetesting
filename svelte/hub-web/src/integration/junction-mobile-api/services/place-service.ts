import type { SessionModel } from "models/user";
import JunctionMobileApiService from "./junction-mobile-api-service";
import { placeParser, type Place, type PlaceSchema } from "../schemas/place";

export class PlaceService extends JunctionMobileApiService {
  async listPlaces({ session, query }: { session: SessionModel; query: string }): Promise<Place[]> {
    const resp = await this.makeRequest<{ data: PlaceSchema[] }>("/places", {
      queryParams: { "query[name]": query },
      session,
    });

    return resp.json.data.map((item) => placeParser.toModel(item));
  }

  async getPlace({ session, id }: { session: SessionModel; id: string }): Promise<Place> {
    const resp = await this.makeRequest<{ data: PlaceSchema }>(`/places/${id}`, { session });

    return placeParser.toModel(resp.json.data);
  }
}
