import type SettingsFlowService from "~/integration/ory/services/settings-flow-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<SettingsFlowService, RequestEvent>(
  "/integration/ory/user-settings",
)({
  complete: (data: Record<string, string>) => [data],
});

export { server };
export default client;
