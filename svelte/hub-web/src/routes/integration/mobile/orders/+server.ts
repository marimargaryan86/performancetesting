import integrationInstances from "~/integration-instances";
import { server } from "./order-service";

export const POST = server({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionMobileApi.orders.create({ session, data });
  },
  createMarkups({ locals: { session } }, { data }) {
    return integrationInstances.junctionMobileApi.orders.createMarkups({ session, data });
  },
  find({ locals: { session } }, { cursor, limit }) {
    return integrationInstances.junctionMobileApi.orders.find({ session, cursor, limit });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionMobileApi.orders.get({ session, id });
  },
  getMarkups({ locals: { session } }, { orderId }) {
    return integrationInstances.junctionMobileApi.orders.getMarkups({ session, orderId });
  },
});
