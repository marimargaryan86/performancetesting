type Place = {
  id: string;
  name: string;
  country: string;
  type?: string;
};
type PlaceFilter = (place: Place) => boolean;

type Passengers = {
  adults: number;
  children: number;
};

type Room = {
  adults: number;
  children: number;
};

export type { Place, PlaceFilter, Passengers, Room };
