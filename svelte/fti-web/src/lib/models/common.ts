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

type IconTypes =
  | "chevron-left"
  | "chevron-right"
  | "plus-icon"
  | "minus-icon"
  | "star"
  | "map-marker"
  | "heart"
  | "calendar"
  | "bed"
  | "take-off"
  | "passenger"
  | "heart-full"
  | "heart-empty"
  | "phone"
  | "menu-bars"
  | "restaurant"
  | "euro"
  | "umbrella"
  | "board-basis-any"
  | "board-basis-all"
  | "board-basis-room"
  | "board-basis-breakfast"
  | "board-basis-half"
  | "board-basis-full"
  | "thumbs-up-down"
  | "hot-tub"
  | "chevron-down";

type SliderRange = {
  from: number;
  to: number;
};

type BoardOptions = {
  title: string;
  icon: IconTypes;
};

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
  IconTypes,
  SliderRange,
  BoardOptions,
};
