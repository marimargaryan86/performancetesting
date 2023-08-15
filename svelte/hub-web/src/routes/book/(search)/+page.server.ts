import integrationInstancesServer from "integration-instances-server";
import type { PlaceModel } from "models/booking/location";

export const actions = {
  async listPlaces(event): Promise<{ places: PlaceModel[] }> {
    const formData = await event.request.formData();
    const query = formData.get("query")?.toString() ?? "";

    if (query.length < 3) {
      return { places: [] };
    }

    return {
      places: await integrationInstancesServer.junctionMobileApi.places.listPlaces(query),
    };
  },
};
