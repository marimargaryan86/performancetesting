import type CompanyService from "~/integration/junction-hub-api/services/company-service";
import type { RequestEvent } from "./$types";
import rpcBase from "../../rpc-base";

const { client, server } = rpcBase<CompanyService, RequestEvent>("/integration/hub/companies")({
  get: (params: { id: string }) => [params],
});

export { server };
export default client;
