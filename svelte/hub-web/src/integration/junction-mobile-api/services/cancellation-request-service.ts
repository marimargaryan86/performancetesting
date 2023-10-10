import type { SessionModel } from "models/user";
import {
  type CreateCancellationRequestModel,
  type CancellationRequestModel,
  type CancellationRequestSchema,
  createCancellationRequestModel,
  cancellationRequestModel,
} from "../schemas/cancellation-request";
import JunctionMobileApiService from "./junction-mobile-api-service";

export class CancellationRequestService extends JunctionMobileApiService {
  async createCancellationRequest({
    session,
    data,
  }: {
    session: SessionModel;
    data: CreateCancellationRequestModel;
  }): Promise<CancellationRequestModel> {
    const resp = await this.makeRequest<{ data: CancellationRequestSchema }>(
      "/cancellations/requests",
      {
        method: "POST",
        data: { data: createCancellationRequestModel.toSchema(data) },
        session,
      },
    );

    return cancellationRequestModel.toModel(resp.json.data);
  }

  async getCancellationRequest({
    id,
    session,
  }: {
    session: SessionModel;
    id: string;
  }): Promise<CancellationRequestModel> {
    const resp = await this.makeRequest<{ data: CancellationRequestSchema }>(
      `/cancellations/requests/${id}`,
      { session },
    );

    return cancellationRequestModel.toModel(resp.json.data);
  }
}
