import type { CuratedPlaceModel, PlaceModel, PlaceSearchData } from "$lib/models/place";
import utils from "$lib/utils";
import faker from "@faker-js/faker";
import BaseService from "./base-service";

// TODO: Remove.
function generatePlace(): PlaceModel {
  return {
    id: faker.datatype.uuid(),
    coordinates: {
      longitude: parseFloat(faker.address.longitude()),
      latitude: parseFloat(faker.address.latitude()),
    },
    countryCode: faker.address.countryCode(),
    name: faker.address.streetName(),
    sourceRef: faker.datatype.uuid(),
    timeZone: faker.address.timeZone(),
    updatedAt: faker.date.past(),
  };
}

// TODO: Remove.
function generateCuratedPlace(): CuratedPlaceModel {
  return {
    ...generatePlace(),
    mergedPlaces: [...Array(faker.datatype.number({ min: 1, max: 13 }))].map(() => generatePlace()),
  };
}

export default class PlaceService extends BaseService {
  async getPlace(placeId: string): Promise<PlaceModel | undefined> {
    // TODO: Impl.
    await utils.sleep(1500);

    return generatePlace();
  }

  async findPlaces(data?: PlaceSearchData, pageOffset = 0, pageLimit = 50): Promise<PlaceModel[]> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (data?.name === "asd" || pageOffset === 5) {
      throw "NO_PLACES_FOUND";
    }

    return [...new Array(pageLimit)].map(() => generatePlace());
  }

  async getCuratedPlace(placeId: string): Promise<CuratedPlaceModel> {
    // TODO: Impl.
    await utils.sleep(1500);

    return generateCuratedPlace();
  }

  async putCuratedPlace(data: Partial<CuratedPlaceModel>): Promise<CuratedPlaceModel> {
    // TODO: Impl.
    await utils.sleep(1500);

    return { ...(data as CuratedPlaceModel) };
  }

  async deleteCuratedPlace(placeId: string): Promise<void> {
    // TODO: Impl.
    await utils.sleep(1500);
  }

  async findCuratedPlaces(
    data?: PlaceSearchData,
    pageOffset = 0,
    pageLimit = 50,
  ): Promise<CuratedPlaceModel[]> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (data?.name === "asd" || pageOffset === 5) {
      throw "NO_CURATED_PLACES_FOUND";
    }

    return [...new Array(pageLimit)].map(() => generateCuratedPlace());
  }
}
