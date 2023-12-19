import type CompanyService from "integration/junction-hub-api/services/company-service";
import { clientServiceFactory } from "../../framework";
import type { RouteId } from "./$types";

const factory = clientServiceFactory<CompanyService, RouteId>("/integration/hub/companies");

export default factory({
  get: (params: { id: string }) => [params],
});
