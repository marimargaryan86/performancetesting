import type { CurrencyModel, FindCriteriaModel } from "../models/currencies";
import { parseCurrencySchema } from "../parsers/currencies";
import type { CurrencySchema, FindCurrenciesResponseSchema } from "../schemas/currencies";
import BaseService from "./base-service";

export default class CurrencyService extends BaseService {
  async find(criteria: FindCriteriaModel): Promise<CurrencyModel[]> {
    const resp = await this.fetch("/v2/reference/currencies");

    switch (resp.status) {
      case 200:
        break;
      case 400:
        throw "BAD_REQUEST";
      default:
        throw "SERVICE_UNAVAILABLE";
    }

    const data: FindCurrenciesResponseSchema = await resp.json();
    const field = criteria.order ?? "code";
    const orderDirection = criteria.orderDirection ?? "asc";
    const limit = criteria.limit ?? 20;
    const offset = (criteria.offset ?? 0) * limit;

    return data.currencies
      .sort((a, b) => {
        if (orderDirection === "asc") {
          return 0 - (a[field as keyof CurrencySchema] < b[field as keyof CurrencySchema] ? 1 : -1);
        }

        return 0 - (a[field as keyof CurrencySchema] > b[field as keyof CurrencySchema] ? 1 : -1);
      })
      .slice(offset, offset + limit)
      .map((item) => parseCurrencySchema(item));
  }

  async get(currencyCode: string): Promise<CurrencyModel> {
    const resp = await this.fetch("/v2/reference/currencies");

    switch (resp.status) {
      case 200:
        break;
      case 400:
        throw "BAD_REQUEST";
      default:
        throw "SERVICE_UNAVAILABLE";
    }

    const data: FindCurrenciesResponseSchema = await resp.json();
    const currency = data.currencies.find((item) => item.code === currencyCode);

    if (!currency) {
      throw "NOT_FOUND";
    }

    return parseCurrencySchema(currency);
  }
}
