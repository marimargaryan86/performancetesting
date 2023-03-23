import type { CompanyModel } from "models/company";
import type { GetCompanyDetailsResponseSchema } from "../schemas/company";
import JunctionPayService from "./junction-pay-service";

export default class CompanyService extends JunctionPayService {
  async getCompanyDetails(token: string, id: string): Promise<CompanyModel> {
    const resp = await fetch(this.getResourceUrl(`/companies/${id}`), {
      headers: this.getHeadersWithAuth(token),
    });

    if (resp.status === 404) {
      throw new Error("Company does not exist");
    }

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as GetCompanyDetailsResponseSchema;

    return {
      id: data.data.id,
      name: data.data.attributes.name,
    };
  }
}
