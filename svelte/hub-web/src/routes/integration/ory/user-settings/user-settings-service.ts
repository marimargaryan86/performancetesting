import { clientServiceFactory } from "../../framework";
import type SettingsFlowService from "integration/ory/services/settings-flow-service";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<SettingsFlowService, RouteId>(
  "/integration/ory/user-settings",
);

export default factory({
  complete: (data: Record<string, string>) => [data],
});
