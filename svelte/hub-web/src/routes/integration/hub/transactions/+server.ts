import integrationInstances from "integration-instances";
import { serverServiceFactory } from "../../framework";
import transactionService from "./transaction-service";

const factory = serverServiceFactory(transactionService);

export const POST = factory({
  find({ locals: { session } }, { cursor, filter, limit, sort }) {
    return integrationInstances.junctionHubApi.transactions.find({
      session,
      limit,
      cursor,
      sort,
      filter,
    });
  },
  get({ locals: { session } }, { id }) {
    return integrationInstances.junctionHubApi.transactions.get({ session, id });
  },
});
