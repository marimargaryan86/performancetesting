import type { SessionModel } from "models/user";
import {
  beneficiaryModel,
  putBeneficiaryModel,
  type BeneficiaryModel,
  type BeneficiarySchema,
} from "../schemas/beneficiary";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";

export default class BeneficiaryService extends JunctionHubApiService {
  async listBeneficiaries({
    session,
    cursor,
  }: {
    session: SessionModel;
    cursor?: string;
  }): Promise<PaginatedData<BeneficiaryModel>> {
    const resp = await this.makeRequest<{
      data: BeneficiarySchema[];
      links: { next: string };
    }>("/beneficiaries", {
      session,
      queryParams: { "page[cursor]": cursor },
    });

    return {
      data: resp.json.data.map(beneficiaryModel.toModel),
      cursor: BeneficiaryService.getCursor(resp.json),
    };
  }

  async getBeneficiary({
    session,
    id,
  }: {
    session: SessionModel;
    id: string;
  }): Promise<BeneficiaryModel> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>(`/beneficiaries/${id}`, {
      session,
    });

    return beneficiaryModel.toModel(resp.json.data);
  }

  async createBeneficiary({
    session,
    beneficiary,
  }: {
    session: SessionModel;
    beneficiary: Omit<BeneficiaryModel, "id">;
  }): Promise<BeneficiaryModel> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>("/beneficiaries", {
      method: "POST",
      session,
      data: { data: putBeneficiaryModel.toSchema(beneficiary) },
    });

    return beneficiaryModel.toModel(resp.json.data);
  }

  async updateBeneficiary({
    session,
    id,
    beneficiary,
  }: {
    session: SessionModel;
    id: string;
    beneficiary: BeneficiaryModel;
  }): Promise<BeneficiaryModel> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>(`/beneficiaries/${id}`, {
      method: "PATCH",
      session,
      data: { data: putBeneficiaryModel.toSchema(beneficiary) },
    });

    return beneficiaryModel.toModel(resp.json.data);
  }
}
