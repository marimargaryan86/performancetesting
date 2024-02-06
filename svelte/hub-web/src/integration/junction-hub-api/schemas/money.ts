import currencyData from "~/data/currency-data";

export type Money = {
  currency: string;
  amount: number;
};

export type MoneySchema = {
  currency: string;
  amount: number;
};

export const moneyParser = {
  toModel: (data: MoneySchema): Money => {
    const currency = currencyData.mapping[data.currency];
    let finalAmount = data.amount;

    if (currency) {
      finalAmount /= 10 ** currency.minorUnits;
    }

    return {
      currency: data.currency,
      amount: finalAmount,
    };
  },
  toSchema: (data: Money): MoneySchema => {
    const currency = currencyData.mapping[data.currency];
    let finalAmount = data.amount;

    if (currency) {
      finalAmount *= 10 ** currency.minorUnits;
    }

    return {
      currency: data.currency,
      amount: Math.round(finalAmount),
    };
  },
};
