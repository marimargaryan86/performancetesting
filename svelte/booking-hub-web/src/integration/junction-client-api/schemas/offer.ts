export interface CabinClassIdentifierSchema {
  id: string;
  type: "cabin-classes";
}

export interface CabinClassSchema extends CabinClassIdentifierSchema {
  attributes: {
    name: string;
  };
  links: { self: string };
}

export interface LegTypeIdentifierSchema {
  id: string;
  type: "leg-types";
}

export interface LegTypeSchema extends LegTypeIdentifierSchema {
  attributes: {
    name: string;
  };
  links: { self: string };
}

export interface QuoteIdentifierSchema {
  id: string;
  type: "trip-offer-price-quotes";
}
