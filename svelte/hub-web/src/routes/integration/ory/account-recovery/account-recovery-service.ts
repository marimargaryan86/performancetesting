import { clientServiceFactory } from "../../framework";
import type RecoveryFlowService from "~/integration/ory/services/recovery-flow-service";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<RecoveryFlowService, RouteId>(
  "/integration/ory/account-recovery",
);

export default factory({
  complete: (data: Record<string, string>) => [data],
});
