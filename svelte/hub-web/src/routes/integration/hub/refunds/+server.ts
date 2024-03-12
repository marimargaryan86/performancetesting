import integrationInstances from "~/integration-instances";
import { server } from "./refund-service";

export const POST = server({
  find({ locals: { session } }, { cursor, limit }) {
    return integrationInstances.junctionHubApi.refunds.find({ session, cursor, limit });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.refunds.get({ session, id });
  },
  getRefundPosition({ locals: { session } }, { data, refundId }) {
    return integrationInstances.junctionHubApi.refunds.getRefundPosition({
      session,
      refundId,
      data,
    });
  },
  update({ locals: { session } }, { data, id }) {
    return integrationInstances.junctionHubApi.refunds.update({ session, data, id });
  },
});
