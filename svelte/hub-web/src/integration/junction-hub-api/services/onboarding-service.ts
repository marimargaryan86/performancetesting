import {
  type OnboardingSchema,
  onboardingParser,
  type OnboardingModel,
} from "../schemas/onboarding";
import JunctionHubApiService from "./junction-hub-api-service";

export default class OnboardingService extends JunctionHubApiService {
  async get(token: string): Promise<OnboardingModel> {
    const result = await this.makeRequest<{ data: OnboardingSchema }>(
      `/onboarding-tokens/${token}`,
    );

    return onboardingParser.toModel(result.json.data);
  }
}
