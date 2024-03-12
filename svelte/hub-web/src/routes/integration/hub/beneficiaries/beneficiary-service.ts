import type BeneficiaryService from "~/integration/junction-hub-api/services/beneficiary-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<BeneficiaryService, RequestEvent>(
  "/integration/hub/beneficiaries",
)({
  create: (params: { data: HubSchemas.BeneficiaryPut }) => [params],
  find: (params: { limit?: number; cursor?: string }) => [params],
  get: (params: { id: string }) => [params],
  update: (params: { id: string; data: HubSchemas.BeneficiaryPut }) => [params],
});

export { server };
export default client;
