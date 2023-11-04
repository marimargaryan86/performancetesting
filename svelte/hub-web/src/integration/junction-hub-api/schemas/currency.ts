export type Currency = {
  code: string;
  name: string;
  minorUnits: number;
};

export type CurrencySchema = {
  id: string;
  type: "currencies";
  attributes: {
    name: string;
    minorUnits: number;
  };
  links: { self: string };
};

export const currencyParser = {
  toModel: (data: CurrencySchema): Currency => ({
    code: data.id,
    name: data.attributes.name,
    minorUnits: data.attributes.minorUnits,
  }),
};
