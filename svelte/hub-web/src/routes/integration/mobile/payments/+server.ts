import integrationInstances from "integration-instances";
import { serverServiceFactory } from "../../framework";
import paymentService from "./payment-service";

const factory = serverServiceFactory(paymentService);

export const POST = factory({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionMobileApi.payments.create({ session, data });
  },
});
