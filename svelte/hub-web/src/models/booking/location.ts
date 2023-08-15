export type CoordinatesModel = {
  lat: number;
  lon: number;
};

export type CountryModel = {
  code: string;
  name?: string;
};

export type PlaceModel = {
  id: string;
  types: string[];
  name: string;
  coordinates: CoordinatesModel;
  timeZone: string;
  iataCode?: string;
  country: CountryModel;
};
