import type { ValidationError } from "$models/common-models";

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
}
