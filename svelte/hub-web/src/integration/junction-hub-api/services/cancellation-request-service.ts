import type * as OrySchemas from "~/integration/ory/schemas";
import JunctionHubApiService from "./junction-hub-api-service";
import {
  cancellationRequestParsers,
  type CancellationRequest,
  type CancellationRequestCreate,
  type CancellationRequestSchema,
} from "../schemas/cancellation";

export default class CancellationRequestService extends JunctionHubApiService {
  async create({
    session,
    data,
  }: {
    session: OrySchemas.Session;
    data: CancellationRequestCreate;
  }): Promise<CancellationRequest> {
    const resp = await this.makeRequest<{ data: CancellationRequestSchema }>(
      "/cancellations/requests",
      {
        session,
        method: "POST",
        data: { data: cancellationRequestParsers.toCreateSchema(data) },
      },
    );

    return cancellationRequestParsers.toModel(resp.json.data);
  }
}
