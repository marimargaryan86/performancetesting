import type LoginFlowService from "~/integration/ory/services/login-flow-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

type Service = {
  login: LoginFlowService["complete"];
  resetLogin(): void;
  logout(): void;
  directLogin(params: { username: string; password: string }): void;
};

const { client, server } = rpcBase<Service, RequestEvent>("/integration/ory/auth")({
  login: (params: { data: Record<string, string>; rememberMe?: boolean }) => [params],
  resetLogin: () => [],
  logout: () => [],
  directLogin: (params: { username: string; password: string }) => [params],
});

export { server };
export default client;
