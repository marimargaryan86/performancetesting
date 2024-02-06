import type PlaceService from "~/integration/junction-mobile-api/services/place-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<PlaceService, RouteId>("/integration/mobile/places");

const methods = factory({
  find: (query: string) => [query],
  get: (params: { id: string }) => [params],
});

type FindMethod = (typeof methods)["find"];

export default {
  ...methods,
  find: (...params: Parameters<FindMethod>): ReturnType<FindMethod> => {
    if (params[0].length < 3) {
      return new Promise((r) => r([]));
    }

    return methods.find(...params);
  },
};
