import type * as OrySchemas from "~/integration/ory/schemas";
import JunctionHubApiService from "./junction-hub-api-service";
import type { PaginatedData } from "$lib/models/common";
import { billParser, type Bill, type BillSchema } from "../schemas/bill";

export default class BillService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
    filter,
  }: {
    session: OrySchemas.Session;
    cursor?: string;
    limit?: number;
    filter?: {
      orderIds?: string[];
    };
  }): Promise<PaginatedData<Bill>> {
    const resp = await this.makeRequest<{
      data: BillSchema[];
      links: { next: string };
    }>("/bills", {
      session,
      queryParams: {
        "filter[order.id][eq]": filter?.orderIds?.join(","),
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

  async get({ session, id }: { session: OrySchemas.Session; id: string }): Promise<Bill> {
    const resp = await this.makeRequest<{ data: BillSchema }>(`/bills/${id}`, { session });

    return billParser.toModel(resp.json.data);
  }

  async toggleReconciliation({
    session,
    bill,
  }: {
    session: OrySchemas.Session;
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
