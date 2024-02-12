import type * as OrySchemas from "~/integration/ory/schemas";
import JunctionMobileApiService from "./junction-mobile-api-service";
import { placeParser, type Place, type PlaceSchema } from "../schemas/place";

export default class PlaceService extends JunctionMobileApiService {
  async find({ session, query }: { session: OrySchemas.Session; query: string }): Promise<Place[]> {
    const resp = await this.makeRequest<{ data: PlaceSchema[] }>("/places", {
      queryParams: { "query[name]": query },
      session,
    });

    return resp.json.data.map((item) => placeParser.toModel(item));
  }

  async get({ session, id }: { session: OrySchemas.Session; id: string }): Promise<Place> {
    const resp = await this.makeRequest<{ data: PlaceSchema }>(`/places/${id}`, { session });

    return placeParser.toModel(resp.json.data);
  }
}
