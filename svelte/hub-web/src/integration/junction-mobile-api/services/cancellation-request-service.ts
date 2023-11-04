import type { SessionModel } from "models/user";
import JunctionMobileApiService from "./junction-mobile-api-service";
import {
  cancellationRequestParsers,
  type CancellationRequest,
  type CancellationRequestCreate,
  type CancellationRequestSchema,
} from "../schemas/cancellation";
import { parseIncluded, type IncludedSchemas } from "../schemas/included";
import { JunctionError } from "integration/common/junction-error";

export default class CancellationRequestService extends JunctionMobileApiService {
  async create({
    session,
    data,
  }: {
    session: SessionModel;
    data: CancellationRequestCreate;
  }): Promise<CancellationRequest> {
    const resp = await this.makeRequest<{ data: CancellationRequestSchema }>(
      "/cancellations/requests",
      {
        method: "POST",
        data: { data: cancellationRequestParsers.toCreateSchema(data) },
        session,
      },
    );

    return cancellationRequestParsers.toModel(resp.json.data);
  }

  async get({ id, session }: { session: SessionModel; id: string }): Promise<CancellationRequest> {
    const resp = await this.makeRequest<{
      data: CancellationRequestSchema;
      included?: IncludedSchemas;
    }>(`/cancellations/requests/${id}`, {
      session,
      queryParams: {
        include: [
          "bookings",
          "bookings.order",
          "bookings.order.journey",
          "bookings.details",
          "bookings.details.cabinClass",
          "bookings.details.legType",
        ].join(","),
      },
    });

    const parsed = parseIncluded([...(resp.json.included ?? []), resp.json.data]);
    const cancellationRequest = parsed.cancellationRequests?.find((item) => item.id === id);

    if (!cancellationRequest) {
      throw new JunctionError({ status: 404, statusText: "Not found" });
    }

    return cancellationRequest;
  }
}
