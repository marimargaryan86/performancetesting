export interface ConversionIdentifierSchema {
  id: string;
  type: "conversions";
}

export interface ConversionSchema extends ConversionIdentifierSchema {
  attributes: {
    settledAt: string;
    rate: number;
  };
}

export interface GetConversionDetailsResponseSchema {
  data: ConversionSchema;
}
