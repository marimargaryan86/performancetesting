import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import {
  beneficiaryParser,
  type Beneficiary,
  type BeneficiarySchema,
  type BeneficiaryPut,
} from "../schemas/beneficiary";

export default class BeneficiaryService extends JunctionHubApiService {
  async listBeneficiaries({
    session,
    cursor,
  }: {
    session: SessionModel;
    cursor?: string;
  }): Promise<PaginatedData<Beneficiary>> {
    const resp = await this.makeRequest<{
      data: BeneficiarySchema[];
      links: { next: string };
    }>("/beneficiaries", {
      session,
      queryParams: { "page[cursor]": cursor },
    });

    return {
      data: resp.json.data.map((item) => beneficiaryParser.toModel(item)),
      cursor: BeneficiaryService.getCursor(resp.json),
    };
  }

  async getBeneficiary({
    session,
    id,
  }: {
    session: SessionModel;
    id: string;
  }): Promise<Beneficiary> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>(`/beneficiaries/${id}`, {
      session,
    });

    return beneficiaryParser.toModel(resp.json.data);
  }

  async createBeneficiary({
    session,
    data,
  }: {
    session: SessionModel;
    data: BeneficiaryPut;
  }): Promise<Beneficiary> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>("/beneficiaries", {
      method: "POST",
      session,
      data: { data: beneficiaryParser.toPutSchema(data) },
    });

    return beneficiaryParser.toModel(resp.json.data);
  }

  async updateBeneficiary({
    session,
    id,
    data,
  }: {
    session: SessionModel;
    id: string;
    data: BeneficiaryPut;
  }): Promise<Beneficiary> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>(`/beneficiaries/${id}`, {
      method: "PATCH",
      session,
      data: { data: beneficiaryParser.toPutSchema(data) },
    });

    return beneficiaryParser.toModel(resp.json.data);
  }
}
