export type PlaceSearchData = {
  name?: string;
  coordinates?: Partial<CoordinatesModel>;
  proximity?: number;
};

export type CoordinatesModel = {
  latitude: number;
  longitude: number;
};

export type PlaceModel = {
  id: string;
  name: string;
  coordinates: CoordinatesModel;
  countryCode: string;
  timeZone: string;
  sourceRef: string;
  updatedAt: Date;
};

export type CuratedPlaceModel = PlaceModel & {
  mergedPlaces: PlaceModel[];
};
