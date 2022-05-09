import type { CuratedPlaceModel, PlaceModel, PlaceSearchData } from "$lib/models/place";
import utils from "$lib/utils";
import BaseService from "./base-service";
import mock from "./mock";

export default class PlaceService extends BaseService {
  async get(placeId: string): Promise<PlaceModel | undefined> {
    // TODO: Impl.
    await utils.sleep(1500);

    return { ...mock.generatePlace(), id: placeId };
  }

  async find(data?: PlaceSearchData, pageOffset = 0, pageLimit = 50): Promise<PlaceModel[]> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (data?.name === "asd" || pageOffset === 5) {
      throw new Error("NO_PLACES_FOUND");
    }

    return [...new Array(pageLimit)].map(() => mock.generatePlace());
  }

  async getCurated(placeId: string): Promise<CuratedPlaceModel> {
    // TODO: Impl.
    await utils.sleep(1500);

    return { ...mock.generateCuratedPlace(), id: placeId };
  }

  async putCurated(data: Partial<CuratedPlaceModel>): Promise<CuratedPlaceModel> {
    // TODO: Impl.
    await utils.sleep(1500);

    return { ...(data as CuratedPlaceModel) };
  }

  async deleteCurated(placeId: string): Promise<void> {
    // TODO: Impl.
    await utils.sleep(1500);
  }

  async findCurated(
    data?: PlaceSearchData,
    pageOffset = 0,
    pageLimit = 50,
  ): Promise<CuratedPlaceModel[]> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (data?.name === "asd" || pageOffset === 5) {
      throw new Error("NO_CURATED_PLACES_FOUND");
    }

    return [...new Array(pageLimit)].map(() => mock.generateCuratedPlace());
  }
}
