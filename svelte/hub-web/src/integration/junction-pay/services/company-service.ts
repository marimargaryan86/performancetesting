import { companyModel, type CompanyModel, type CompanySchema } from "../schemas/company";
import JunctionPayService from "./junction-pay-service";

export default class CompanyService extends JunctionPayService {
  async getCompanyDetails(token: string, id: string): Promise<CompanyModel> {
    const resp = await this.makeRequest<{ data: CompanySchema }>(`/companies/${id}`, {
      token,
    });

    return companyModel.toModel(resp.json.data);
  }
}
