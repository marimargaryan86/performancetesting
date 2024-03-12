import integrationInstances from "~/integration-instances";
import { server } from "./payment-service";

export const POST = server({
  create({ locals: { session } }, { data }) {
    return integrationInstances.junctionMobileApi.payments.create({ session, data });
  },
});
