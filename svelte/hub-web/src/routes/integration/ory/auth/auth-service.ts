import type LoginFlowService from "~/integration/ory/services/login-flow-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

type Service = {
  login: LoginFlowService["complete"];
  resetLogin(): void;
  logout(): void;
};

const { client, server } = rpcBase<Service, RequestEvent>("/integration/ory/auth")({
  login: (params: { data: Record<string, string>; rememberMe?: boolean }) => [params],
  resetLogin: () => [],
  logout: () => [],
});

export { server };
export default client;
