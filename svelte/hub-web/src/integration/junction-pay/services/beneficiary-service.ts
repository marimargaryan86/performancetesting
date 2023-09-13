import {
  beneficiaryModel,
  putBeneficiaryModel,
  type BeneficiaryModel,
  type BeneficiarySchema,
} from "../schemas/beneficiary";
import JunctionPayService from "./junction-pay-service";
import type { PaginatedData } from "models/common";

export default class BeneficiaryService extends JunctionPayService {
  async listBeneficiaries(
    token: string,
    cursor?: string,
  ): Promise<PaginatedData<BeneficiaryModel>> {
    const resp = await this.makeRequest<{
      data: BeneficiarySchema[];
      links: { next: string };
    }>("/beneficiaries", {
      token,
      queryParams: { "page[cursor]": cursor },
    });

    return {
      data: resp.json.data.map(beneficiaryModel.toModel),
      cursor: BeneficiaryService.getCursor(resp.json),
    };
  }

  async getBeneficiary(token: string, id: string): Promise<BeneficiaryModel> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>(`/beneficiaries/${id}`, {
      token,
    });

    return beneficiaryModel.toModel(resp.json.data);
  }

  async createBeneficiary(
    token: string,
    beneficiary: Omit<BeneficiaryModel, "id">,
  ): Promise<BeneficiaryModel> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>("/beneficiaries", {
      method: "POST",
      token,
      data: { data: putBeneficiaryModel.toSchema(beneficiary) },
    });

    return beneficiaryModel.toModel(resp.json.data);
  }

  async updateBeneficiary(
    token: string,
    id: string,
    beneficiary: BeneficiaryModel,
  ): Promise<BeneficiaryModel> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>(`/beneficiaries/${id}`, {
      method: "PATCH",
      token,
      data: { data: putBeneficiaryModel.toSchema(beneficiary) },
    });

    return beneficiaryModel.toModel(resp.json.data);
  }
}
