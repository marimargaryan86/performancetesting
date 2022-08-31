import type { CurrencyModel, TradeType } from "../models/currencies";
import type { CurrencySchema } from "../schemas/currencies";

export function parseCurrencySchema(currency: CurrencySchema): CurrencyModel {
  const tradeTypes: TradeType[] = [];

  if (currency.can_buy) {
    tradeTypes.push("buy");
  }

  if (currency.can_sell) {
    tradeTypes.push("sell");
  }

  return {
    code: currency.code,
    decimals: currency.decimal_places,
    name: currency.name,
    tradable: currency.online_trading,
    tradeTypes,
  };
}
