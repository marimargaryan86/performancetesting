import type RecoveryFlowService from "~/integration/ory/services/recovery-flow-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<RecoveryFlowService, RequestEvent>(
  "/integration/ory/account-recovery",
)({
  complete: (data: Record<string, string>) => [data],
});

export { server };
export default client;
