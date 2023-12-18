import integrationInstances from "integration-instances";
import { serverServiceFactory } from "../../framework";
import companyService from "./company-service";

const factory = serverServiceFactory(companyService);

export const POST = factory({
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.companies.get({ session, id });
  },
});
