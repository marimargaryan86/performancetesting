import integrationInstances from "~/integration-instances";
import { serverServiceFactory } from "../../framework";
import refundService from "./refund-service";

const factory = serverServiceFactory(refundService);

export const POST = factory({
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
