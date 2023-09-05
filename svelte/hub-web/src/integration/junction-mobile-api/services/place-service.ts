import { placeModel } from "../schemas/place";
import JunctionMobileApiService from "./junction-mobile-api-service";
import type { Infer } from "../schema-model.server";

export class PlaceService extends JunctionMobileApiService {
  async listPlaces(query: string): Promise<Infer<typeof placeModel>[]> {
    const resp = await this.makeRequest<{ data: Infer<typeof placeModel, "schema">[] }>("/places", {
      queryParams: { "query[name]": query },
    });

    return (await resp.json()).data.map((item) => placeModel.toModel(item));
  }

  async getPlace(id: string): Promise<Infer<typeof placeModel>> {
    const resp = await this.makeRequest<{ data: Infer<typeof placeModel, "schema"> }>(
      `/places/${id}`,
    );

    if (resp.status === 404) {
      throw new Error("Place not found");
    }

    return placeModel.toModel((await resp.json()).data);
  }
}
