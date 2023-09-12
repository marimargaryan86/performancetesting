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

    if (resp.status !== 200) {
      throw new Error(await resp.text());
    }

    const data = await resp.json();

    return {
      data: data.data.map(beneficiaryModel.toModel),
      cursor: BeneficiaryService.getCursor(data),
    };
  }

  async getBeneficiary(token: string, id: string): Promise<BeneficiaryModel> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>(`/beneficiaries/${id}`, {
      token,
    });

    if (resp.status === 404) {
      throw new Error("Beneficiary not found");
    }

    if (resp.status !== 200) {
      throw new Error(await resp.text());
    }

    return beneficiaryModel.toModel((await resp.json()).data);
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

    if (resp.status !== 201) {
      throw new Error(await resp.text());
    }

    const data = await resp.json();

    return beneficiaryModel.toModel(data.data);
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

    if (resp.status !== 200) {
      throw new Error(await resp.text());
    }

    const data = await resp.json();

    return beneficiaryModel.toModel(data.data);
  }
}
