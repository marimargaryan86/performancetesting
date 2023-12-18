import integrationInstances from "integration-instances";
import { serverServiceFactory } from "../../framework";
import currencyService from "./currency-service";

const factory = serverServiceFactory(currencyService);

export const POST = factory({
  find({ locals: { session } }, { cursor, limit }) {
    return integrationInstances.junctionHubApi.currencies.find({ session, cursor, limit });
  },
});
