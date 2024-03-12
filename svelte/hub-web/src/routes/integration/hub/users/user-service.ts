import type UserService from "~/integration/junction-hub-api/services/user-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<UserService, RequestEvent>("/integration/hub/users")({
  create: (params: { data: HubSchemas.UserCreate }) => [params],
  find: (params: { cursor?: string; limit?: number }) => [params],
  get: (params: { id: string }) => [params],
  getProfile: () => [],
  remove: (params: { id: string }) => [params],
  update: (params: { id: string; data: HubSchemas.UserUpdate }) => [params],
});

export { server };
export default client;
