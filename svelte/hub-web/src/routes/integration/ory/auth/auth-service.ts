import { clientServiceFactory } from "../../framework";
import type LoginFlowService from "integration/ory/services/login-flow-service";
import type { RouteId } from "./$types";

type Service = {
  login: LoginFlowService["complete"];
  resetLogin(): void;
  logout(): void;
};

const factory = clientServiceFactory<Service, RouteId>("/integration/ory/auth");

export default factory({
  login: (params: { data: Record<string, string>; rememberMe?: boolean }) => [params],
  resetLogin: () => [],
  logout: () => [],
});
