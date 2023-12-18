import type TransactionService from "integration/junction-hub-api/services/transaction-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<TransactionService, RouteId>("/integration/hub/transactions");

export default factory<{
  find: [
    params: {
      cursor?: string;
      limit?: number;
      sort?: Parameters<TransactionService["find"]>[0]["sort"];
      filter?: Parameters<TransactionService["find"]>[0]["filter"];
    },
  ];
  get: [params: { id: string }];
}>({
  find: true,
  get: true,
});
