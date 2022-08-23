import storage from "$lib/storage";
import type { ValidationError } from "$models/common-models";
import config from "$src/config";

export default abstract class BaseService {
  protected baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  protected containsNoErrors<TData extends Record<string, unknown>>(
    errors: ValidationError<TData>,
  ): boolean {
    return Object.keys(errors).reduce((prev, curr) => prev && !errors[curr], true);
  }

  protected async getApiKey(): Promise<string> {
    let apiKey: string | undefined;
    let expiresAt: Date;

    try {
      ({ value: apiKey, expiresAt } = storage.local.get(
        "cc_api_key",
        (value: { value: string; expiresAt: Date }) => ({
          ...value,
          expiresAt: new Date(value.expiresAt),
        }),
      ));

      if (new Date() > expiresAt) {
        apiKey = undefined;
      }
    } catch {
      apiKey = undefined;
    }

    if (apiKey) {
      return apiKey;
    }

    const formData = new FormData();
    formData.append("login_id", config.CC_LOGIN_ID);
    formData.append("api_key", config.CC_API_KEY);

    const resp = await fetch(new URL("/authenticate/api", config.CC_API_BASE_URL), {
      body: formData,
      method: "POST",
    });

    apiKey = (await resp.json()) as string;
    expiresAt = new Date();
    expiresAt.setTime(expiresAt.getTime() + 1800000);

    storage.local.put("cc_api_key", { value: apiKey, expiresAt });

    return apiKey;
  }
}
