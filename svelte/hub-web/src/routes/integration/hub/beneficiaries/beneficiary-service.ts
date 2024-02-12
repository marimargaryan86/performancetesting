import type BeneficiaryService from "~/integration/junction-hub-api/services/beneficiary-service";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<BeneficiaryService, RouteId>("/integration/hub/beneficiaries");

export default factory({
  create: (params: { data: HubSchemas.BeneficiaryPut }) => [params],
  find: (params: { limit?: number; cursor?: string }) => [params],
  get: (params: { id: string }) => [params],
  update: (params: { id: string; data: HubSchemas.BeneficiaryPut }) => [params],
});
