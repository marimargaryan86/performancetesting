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

type Package = {
  name: string;
  description: string;
  stars: number;
  price: string;
  image: string;
  like: boolean;
};

type FeaturedPackage = {
  name: string;
  location: string;
  length: string;
  stars: number;
  price: string;
  description: string;
};

type WeatherHoliday = {
  name: string;
  rainChance: number;
  sunChance: number;
  temperature: number;
  image: string;
  like: boolean;
};

type LandingPageModel = {
  data: {
    holidayPackages: Package[];
    holidayCategories: string[];
    featuredPackages: FeaturedPackage[];
    weatherHolidays: WeatherHoliday[];
  };
};

type SearchOptions = {
  destination: string;
  origin: string;
  searchType: string;
  passengers: Passengers;
  rooms?: Room[];
  dates?: {
    start: string;
    end: string;
  };
};

type Scroll = {
  changePosition?: (e: CustomEvent) => void;
};

type SelectedDate =
  | {
      start?: string;
      end?: string;
    }
  | {
      date: string;
    }
  | undefined;

export type {
  Place,
  PlaceFilter,
  Passengers,
  Room,
  Package,
  LandingPageModel,
  FeaturedPackage,
  WeatherHoliday,
  SearchOptions,
  Scroll,
  SelectedDate,
};
