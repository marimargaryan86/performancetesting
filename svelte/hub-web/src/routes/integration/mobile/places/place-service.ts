import type PlaceService from "~/integration/junction-mobile-api/services/place-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<PlaceService, RequestEvent>("/integration/mobile/places")({
  find: (query: string) => [query],
  get: (params: { id: string }) => [params],
});

type FindMethod = (typeof client)["find"];

export { server };
export default {
  ...client,
  find: (...params: Parameters<FindMethod>): ReturnType<FindMethod> => {
    if (params[0].length < 3) {
      return new Promise((r) => r([]));
    }

    return client.find(...params);
  },
};
