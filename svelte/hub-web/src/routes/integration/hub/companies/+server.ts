import integrationInstances from "~/integration-instances";
import { server } from "./company-service";

export const POST = server({
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.companies.get({ session, id });
  },
});
