import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import { companyParser, type Company, type CompanySchema } from "../schemas/company";

export default class CompanyService extends JunctionHubApiService {
  async getCompanyDetails({
    session,
    id,
  }: {
    session: SessionModel;
    id: string;
  }): Promise<Company> {
    const resp = await this.makeRequest<{ data: CompanySchema }>(`/companies/${id}`, {
      session,
    });

    return companyParser.toModel(resp.json.data);
  }
}
