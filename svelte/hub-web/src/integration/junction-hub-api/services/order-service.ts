import type { Session } from "integration/ory/schemas";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";
import type { OrderSchema, Order } from "../schemas/order";
import JunctionHubApiService from "./junction-hub-api-service";
import { JunctionError } from "integration/common/junction-error";

export default class OrderService extends JunctionHubApiService {
  async get({ session, id }: { session: Session; id: string }): Promise<Order> {
    const resp = await this.makeRequest<{ data: OrderSchema; included?: IncludedSchemas }>(
      `/orders/${id}`,
      {
        session,
        queryParams: {
          include: [
            "journey",
            "bookings",
            "bookings.details",
            "bookings.bookingCancellation",
            "bookings.transaction",
            "bookings.refund",
          ].join(","),
        },
      },
    );

    const parsed = parseIncluded([...(resp.json.included ?? []), resp.json.data]);
    const order = parsed.orders?.find((item) => item.id === id);

    if (!order) {
      throw new JunctionError({ status: 404, statusText: "Not found" });
    }

    return order;
  }
}
