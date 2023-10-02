import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import { billModel, type BillModel, type BillSchema } from "../schemas/bill";

export class BillService extends JunctionHubApiService {
  async listBills({
    session,
    cursor,
    limit = 100,
  }: {
    session: SessionModel;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<BillModel>> {
    const resp = await this.makeRequest<{
      data: BillSchema[];
      links: { next: string };
    }>("/bills", {
      session,
      queryParams: {
        "page[cursor]": cursor,
        "page[limit]": limit,
      },
    });

    return {
      data: resp.json.data.map(billModel.toModel),
      cursor: BillService.getCursor(resp.json),
    };
  }

  async getBill({
    session,
    billId,
  }: {
    session: SessionModel;
    billId: string;
  }): Promise<BillModel> {
    const resp = await this.makeRequest<{ data: BillSchema }>(`/bills/${billId}`, { session });

    return billModel.toModel(resp.json.data);
  }

  async toggleReconciliation({
    session,
    bill,
  }: {
    session: SessionModel;
    bill: BillModel;
  }): Promise<BillModel> {
    const resp = await this.makeRequest<{
      data: BillSchema;
    }>(`/bills/${bill.id}`, {
      session,
      method: "PATCH",
      data: {
        data: {
          type: "bills",
          attributes: { isReconciled: !bill.isReconciled },
        },
      },
    });

    return billModel.toModel(resp.json.data);
  }
}
