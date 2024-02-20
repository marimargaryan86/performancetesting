import type UserService from "~/integration/junction-hub-api/services/user-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<UserService, RouteId>("/integration/hub/users");

export default factory({
  create: (params: { data: HubSchemas.UserCreate }) => [params],
  find: (params: { cursor?: string; limit?: number }) => [params],
  get: (params: { id: string }) => [params],
  getProfile: () => [],
  remove: (params: { id: string }) => [params],
  update: (params: { id: string; data: HubSchemas.UserUpdate }) => [params],
});
