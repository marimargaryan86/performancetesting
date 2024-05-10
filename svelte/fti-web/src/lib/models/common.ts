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
  origin: string | undefined;
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

type SliderRange = {
  from: number;
  to: number;
};

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
  | "chevron-down"
  | "half-moon"
  | "beach"
  | "wifi"
  | "pool"
  | "parking"
  | "bar"
  | "gym"
  | "spa"
  | "tick"
  | "flight"
  | "hotel"
  | "transfer"
  | "luggage"
  | "copy-icon"
  | "email-icon"
  | "message-icon"
  | "location-icon"
  | "share-icon"
  | "left-back-arrow"
  | "back-icon"
  | "forward-icon";

type AmenityIcons = "wifi" | "pool" | "parking" | "restaurant" | "bar" | "gym" | "beach" | "spa";

type Amenities = {
  label: string;
  icon: AmenityIcons;
};

type BoardOptions = {
  title: string;
  icon: IconTypes;
};

/** @deprecated use specific search result type instead */
type SearchResultTile = {
  name: string;
  location: string;
  rating: number;
  reviews: number;
  checkIn: string;
  checkOut: string;
  cancellationFee: string;
  amenities: Amenities[];
  rebook: string;
  included: IconTypes[];
  price: number;
  favourite: boolean;
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
  SearchResultTile,
  IconTypes,
  AmenityIcons,
  SliderRange,
  BoardOptions,
};
