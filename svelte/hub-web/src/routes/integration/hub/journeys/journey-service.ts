import type JourneyService from "~/integration/junction-hub-api/services/journey-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<JourneyService, RequestEvent>("/integration/hub/journeys")({
  find: (params: {
    cursor?: string;
    limit?: number;
    sort?: Parameters<JourneyService["find"]>[0]["sort"];
    filter?: Parameters<JourneyService["find"]>[0]["filter"];
  }) => [params],
});

export { server };
export default client;
