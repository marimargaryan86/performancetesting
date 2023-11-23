import type { Session } from "integration/ory/schemas/authentication";
import JunctionHubApiService from "./junction-hub-api-service";
import { companyParser, type Company, type CompanySchema } from "../schemas/company";

export default class CompanyService extends JunctionHubApiService {
  async get({ session, id }: { session: Session; id: string }): Promise<Company> {
    const resp = await this.makeRequest<{ data: CompanySchema }>(`/companies/${id}`, {
      session,
    });

    return companyParser.toModel(resp.json.data);
  }
}
