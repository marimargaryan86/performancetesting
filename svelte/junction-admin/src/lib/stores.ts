import { writable } from "svelte/store";
import type { CuratedPlaceModel } from "./models/place";
import utils from "./utils";

const CURATED_PLACE = "CURATED_PLACE";

export const curatedPlaceStore = writable<
  (CuratedPlaceModel & { removeExisting?: string[] }) | undefined
>(
  utils.storage.get(
    CURATED_PLACE,
    (data): CuratedPlaceModel =>
      ({ ...data, updatedAt: new Date(data.updatedAt as string) } as CuratedPlaceModel),
  ),
);

curatedPlaceStore.subscribe((curatedPlace) => {
  if (!curatedPlace) {
    utils.storage.remove(CURATED_PLACE);
  } else {
    utils.storage.set(CURATED_PLACE, curatedPlace);
  }
});
