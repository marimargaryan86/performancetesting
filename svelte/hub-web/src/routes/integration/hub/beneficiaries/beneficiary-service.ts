import type BeneficiaryService from "integration/junction-hub-api/services/beneficiary-service";
import type { BeneficiaryPut } from "integration/junction-hub-api/schemas/beneficiary";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<BeneficiaryService, RouteId>("/integration/hub/beneficiaries");

export default factory<{
  create: [params: { data: BeneficiaryPut }];
  find: [params: { limit?: number; cursor?: string }];
  get: [params: { id: string }];
  update: [params: { id: string; data: BeneficiaryPut }];
}>({
  create: true,
  find: true,
  get: true,
  update: true,
});
