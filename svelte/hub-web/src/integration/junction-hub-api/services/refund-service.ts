import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import { refundParser, type Refund, type RefundSchema, type RefundPut } from "../schemas/refund";

export default class RefundService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
  }: {
    session: SessionModel;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<Refund>> {
    const resp = await this.makeRequest<{ data: RefundSchema[]; links: { next: string } }>(
      "/refunds",
      {
        session,
        queryParams: {
          "page[cursor]": cursor,
          "page[limit]": limit,
        },
      },
    );

    return {
      data: resp.json.data.map((item) => refundParser.toModel(item)),
      cursor: RefundService.getCursor(resp.json),
    };
  }

  async get({ session, id }: { session: SessionModel; id: string }): Promise<Refund> {
    const resp = await this.makeRequest<{ data: RefundSchema }>(`/refunds/${id}`, {
      session,
    });

    return refundParser.toModel(resp.json.data);
  }

  async create({ session, data }: { session: SessionModel; data: RefundPut }): Promise<Refund> {
    const resp = await this.makeRequest<{ data: RefundSchema }>("/refunds", {
      session,
      data: { data: refundParser.toPutSchema(data) },
      method: "POST",
    });

    return refundParser.toModel(resp.json.data);
  }

  async update({
    session,
    data,
    id,
  }: {
    session: SessionModel;
    data: RefundPut;
    id: string;
  }): Promise<Refund> {
    const resp = await this.makeRequest<{ data: RefundSchema }>(`/refunds/${id}`, {
      session,
      data: { data: refundParser.toPutSchema(data) },
      method: "PATCH",
    });

    return refundParser.toModel(resp.json.data);
  }
}
