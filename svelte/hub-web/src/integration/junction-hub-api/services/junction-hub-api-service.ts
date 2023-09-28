import JunctionService from "integration/common/junction-service";
import type { SessionModel } from "models/user";

export default abstract class JunctionHubApiService extends JunctionService {
  protected override makeRequest<TResp = unknown>(
    resource: string,
    options?: {
      method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
      queryParams?: Record<string, string | number | undefined>;
      headers?: Record<string, string>;
      data?: unknown;
      session: SessionModel;
    },
  ): Promise<Omit<Response, "json"> & { json: TResp }> {
    return super.makeRequest(resource, options);
  }
}
