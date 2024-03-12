import integrationInstances from "~/integration-instances";
import { server } from "./beneficiary-service";

export const POST = server({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionHubApi.beneficiaries.create({ session, data });
  },
  find({ locals: { session } }, { cursor, limit }) {
    return integrationInstances.junctionHubApi.beneficiaries.find({ session, cursor, limit });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.beneficiaries.get({ session, id });
  },
  update({ locals: { session } }, { id, data }) {
    return integrationInstances.junctionHubApi.beneficiaries.update({ session, id, data });
  },
});
