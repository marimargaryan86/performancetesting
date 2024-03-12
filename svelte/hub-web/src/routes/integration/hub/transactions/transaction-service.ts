import type TransactionService from "~/integration/junction-hub-api/services/transaction-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<TransactionService, RequestEvent>(
  "/integration/hub/transactions",
)({
  find: (params: {
    cursor?: string;
    limit?: number;
    sort?: Parameters<TransactionService["find"]>[0]["sort"];
    filter?: Parameters<TransactionService["find"]>[0]["filter"];
  }) => [params],
  get: (params: { id: string }) => [params],
});

export { server };
export default client;
