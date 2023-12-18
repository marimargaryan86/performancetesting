import integrationInstances from "integration-instances";
import { serverServiceFactory } from "../../framework";
import conversionService from "./conversion-service";

const factory = serverServiceFactory(conversionService);

export const POST = factory({
  find({ locals: { session } }, { cursor, limit }) {
    return integrationInstances.junctionHubApi.conversions.find({ session, cursor, limit });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.conversions.get({ session, id });
  },
});
