import type { SessionModel } from "models/user";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "models/common";
import { billParser, type Bill, type BillSchema } from "../schemas/bill";

export default class BillService extends JunctionHubApiService {
  async listBills({
    session,
    cursor,
    limit = 100,
  }: {
    session: SessionModel;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<Bill>> {
    const resp = await this.makeRequest<{
      data: BillSchema[];
      links: { next: string };
    }>("/bills", {
      session,
      queryParams: {
        "page[cursor]": cursor,
        "page[limit]": limit,
        sort: "-updatedAt",
      },
    });

    return {
      data: resp.json.data.map((item) => billParser.toModel(item)),
      cursor: BillService.getCursor(resp.json),
    };
  }

  async getBill({ session, billId }: { session: SessionModel; billId: string }): Promise<Bill> {
    const resp = await this.makeRequest<{ data: BillSchema }>(`/bills/${billId}`, { session });

    return billParser.toModel(resp.json.data);
  }

  async toggleReconciliation({
    session,
    bill,
  }: {
    session: SessionModel;
    bill: Bill;
  }): Promise<Bill> {
    const resp = await this.makeRequest<{
      data: BillSchema;
    }>(`/bills/${bill.id}`, {
      session,
      method: "PATCH",
      data: {
        data: billParser.toUpdateSchema({ ...bill, reconciled: !bill.reconciled }),
      },
    });

    return billParser.toModel(resp.json.data);
  }
}
