import utils from "$lib/utils";
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

  protected buildUrl(url: string, params?: Record<string, string | number>): URL {
    const nextUrl = `${this.baseUrl}${url}`;
    const result = new URL(nextUrl);

    if (params) {
      Object.entries(params).forEach(([key, val]) => result.searchParams.set(key, val.toString()));
    }

    return result;
  }

  protected async loginAndReturnApiKey() {
    const api_key = utils.fetchAndCheckLocalStorageWithExpiry("cc_api_key");
    if (!api_key) {
      const formData = new FormData();
      formData.append("login_id", config.CC_LOGIN_ID);
      formData.append("api_key", config.CC_API_KEY);
      const response = await fetch("https://devapi.currencycloud.com/v2/authenticate/api", {
        body: formData,
        method: "POST",
      });
      const apiKey = await response.json();
      utils.setLocalStorageWithExpiry("cc_api_key", apiKey, 30 * 60000);
      return apiKey;
    }
    return api_key;
  }
}
