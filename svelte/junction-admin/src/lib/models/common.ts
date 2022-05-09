export type CoordinatesModel = {
  latitude: number;
  longitude: number;
};

export type PriceModel = {
  currency: string;
  total: number;
  tax?: number;
};
