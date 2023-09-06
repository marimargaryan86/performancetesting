import integrationInstances from "integration-instances";
import type { PlaceModel } from "integration/junction-mobile-api/schemas/place";

export const actions = {
  async listPlaces(event): Promise<{ places: PlaceModel[] }> {
    const formData = await event.request.formData();
    const query = formData.get("query")?.toString() ?? "";

    if (query.length < 3) {
      return { places: [] };
    }

    return {
      places: await integrationInstances.junctionMobileApi.places.listPlaces(query),
    };
  },
};
