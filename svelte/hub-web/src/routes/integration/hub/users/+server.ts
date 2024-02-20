import integrationInstancesServer from "~/integration-instances";
import { serverServiceFactory } from "../../framework";
import userService from "./user-service";

const factory = serverServiceFactory(userService);

export const POST = factory({
  create({ locals: { session } }, { data }) {
    return integrationInstancesServer.junctionHubApi.users.create({ session, data });
  },
  find({ locals: { session } }, { cursor, limit }) {
    return integrationInstancesServer.junctionHubApi.users.find({ session, cursor, limit });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstancesServer.junctionHubApi.users.get({ session, id });
  },
  getProfile({ locals: { session } }) {
    return integrationInstancesServer.junctionHubApi.users.getProfile({ session });
  },
  remove({ locals: { session } }, { id }) {
    return integrationInstancesServer.junctionHubApi.users.remove({ session, id });
  },
  update({ locals: { session } }, { id, data }) {
    return integrationInstancesServer.junctionHubApi.users.update({ session, id, data });
  },
});
