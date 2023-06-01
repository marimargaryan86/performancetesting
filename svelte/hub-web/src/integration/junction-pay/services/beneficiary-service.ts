import type { BeneficiaryModel } from "models/beneficiary";
import { parseBeneficiarySchema } from "../parsers/beneficiary";
import type {
  CreateBeneficiaryResponseSchema,
  GetBeneficiaryResponseSchema,
  ListBeneficiariesResponseSchema,
} from "../schemas/beneficiaty";
import JunctionPayService from "./junction-pay-service";
import type { PaginatedData } from "models/common";

export default class BeneficiaryService extends JunctionPayService {
  async listBeneficiaries(
    token: string,
    cursor?: string,
  ): Promise<PaginatedData<BeneficiaryModel>> {
    const resp = await this.makeRequest<ListBeneficiariesResponseSchema>("/beneficiaries", {
      token,
      queryParams: { "page[cursor]": cursor },
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = await resp.json();

    return {
      data: data.data.map(parseBeneficiarySchema),
      cursor: BeneficiaryService.getCursor(data),
    };
  }

  async getBeneficiary(token: string, id: string): Promise<BeneficiaryModel> {
    const resp = await this.makeRequest<GetBeneficiaryResponseSchema>(`/beneficiaries/${id}`, {
      token,
    });

    if (resp.status === 404) {
      throw new Error("Beneficiary not found");
    }

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    return parseBeneficiarySchema((await resp.json()).data);
  }

  async createBeneficiary(token: string, beneficiary: unknown): Promise<BeneficiaryModel> {
    const resp = await this.makeRequest("/beneficiaries", {
      method: "POST",
      token,
      data: beneficiary,
    });

    if (resp.status !== 201) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    const data = (await resp.json()) as CreateBeneficiaryResponseSchema;

    return parseBeneficiarySchema(data.data);
  }
}
