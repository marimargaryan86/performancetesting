import {
  type CreateCancellationRequestModel,
  type CancellationRequestModel,
  type CancellationRequestSchema,
  createCancellationRequestModel,
  cancellationRequestModel,
} from "../schemas/cancellation-request";
import JunctionMobileApiService from "./junction-mobile-api-service";

export class CancellationRequestService extends JunctionMobileApiService {
  async createCancellationRequest(
    data: CreateCancellationRequestModel,
  ): Promise<CancellationRequestModel> {
    const resp = await this.makeRequest<{ data: CancellationRequestSchema }>(
      "/cancellations/requests",
      {
        method: "POST",
        data: { data: createCancellationRequestModel.toSchema(data) },
      },
    );

    return cancellationRequestModel.toModel(resp.json.data);
  }

  async getCancellationRequest(id: string): Promise<CancellationRequestModel> {
    const resp = await this.makeRequest<{ data: CancellationRequestSchema }>(
      `/cancellations/requests/${id}`,
    );

    return cancellationRequestModel.toModel(resp.json.data);
  }
}
