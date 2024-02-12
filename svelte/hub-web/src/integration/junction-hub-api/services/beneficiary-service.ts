import type { Session } from "~/integration/ory/schemas/authentication";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "$lib/models/common";
import {
  beneficiaryParser,
  type Beneficiary,
  type BeneficiarySchema,
  type BeneficiaryPut,
} from "../schemas/beneficiary";

export default class BeneficiaryService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
  }: {
    session: Session;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<Beneficiary>> {
    const resp = await this.makeRequest<{
      data: BeneficiarySchema[];
      links: { next: string };
    }>("/beneficiaries", {
      session,
      queryParams: { "page[cursor]": cursor, "page[limit]": limit },
    });

    return {
      data: resp.json.data.map((item) => beneficiaryParser.toModel(item)),
      cursor: BeneficiaryService.getCursor(resp.json),
    };
  }

  async get({ session, id }: { session: Session; id: string }): Promise<Beneficiary> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>(`/beneficiaries/${id}`, {
      session,
    });

    return beneficiaryParser.toModel(resp.json.data);
  }

  async create({
    session,
    data,
  }: {
    session: Session;
    data: BeneficiaryPut;
  }): Promise<Beneficiary> {
    const resp = await this.makeRequest<{ data: BeneficiarySchema }>("/beneficiaries", {
      method: "POST",
      session,
      data: { data: beneficiaryParser.toPutSchema(data) },
    });

    return beneficiaryParser.toModel(resp.json.data);
  }

  async update({
    session,
    id,
    data,
  }: {
    session: Session;
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
