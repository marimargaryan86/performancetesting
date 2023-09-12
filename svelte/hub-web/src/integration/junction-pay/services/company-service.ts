import { companyModel, type CompanyModel, type CompanySchema } from "../schemas/company";
import JunctionPayService from "./junction-pay-service";

export default class CompanyService extends JunctionPayService {
  async getCompanyDetails(token: string, id: string): Promise<CompanyModel> {
    const resp = await this.makeRequest<{ data: CompanySchema }>(`/companies/${id}`, {
      token,
    });

    if (resp.status === 404) {
      throw new Error("Company does not exist");
    }

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = await resp.json();

    return companyModel.toModel(data.data);
  }
}
