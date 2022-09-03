import type { CurrencyModel } from "$integration/currency-cloud/models/currencies";

export default class CurrencyService {
  async find(): Promise<CurrencyModel[]> {
    if (typeof window === "undefined") {
      return [];
    }

    return await (await fetch(new URL("/api/currencies", window.location.origin))).json();
  }
}
