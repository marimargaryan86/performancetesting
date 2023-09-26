import integrationInstances from "integration-instances";
import type { PlaceModel } from "integration/junction-mobile-api/schemas/place";
import { getActionRequestJsonData } from "utils/common";
import { tripSearchData } from "../../components/trip-search/trip-search.svelte";
import { ActionFailure, fail } from "@sveltejs/kit";
import bookingManager from "../booking-manager.server";

function requiresPrecision(place: PlaceModel): boolean {
  return !(place.types.includes("city") || place.types.includes("unspecified"));
}

export const actions = {
  async search(event): Promise<void | ActionFailure> {
    try {
      const searchData = await getActionRequestJsonData(event, tripSearchData);
      const [origin, destination] = await Promise.all([
        integrationInstances.junctionMobileApi.places.getPlace(searchData.originId),
        integrationInstances.junctionMobileApi.places.getPlace(searchData.destinationId),
      ]);

      bookingManager.setSearchData(
        {
          ...searchData,
          outbound: searchData.outbound,
          origin: {
            ...origin.coordinates,
            id: origin.id,
            precise: requiresPrecision(origin),
          },
          destination: {
            ...destination.coordinates,
            id: destination.id,
            precise: requiresPrecision(destination),
          },
          passengers: searchData.passengers,
        },
        event,
      );
    } catch {
      return fail(400);
    }
  },
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
