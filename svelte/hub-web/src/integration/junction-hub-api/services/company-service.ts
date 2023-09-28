import type { SessionModel } from "models/user";
import { companyModel, type CompanyModel, type CompanySchema } from "../schemas/company";
import JunctionHubApiService from "./junction-hub-api-service";

export default class CompanyService extends JunctionHubApiService {
  async getCompanyDetails({
    session,
    id,
  }: {
    session: SessionModel;
    id: string;
  }): Promise<CompanyModel> {
    const resp = await this.makeRequest<{ data: CompanySchema }>(`/companies/${id}`, {
      session,
    });

    return companyModel.toModel(resp.json.data);
  }
}
