import type { Place } from "$lib/models/common";

const weatherCategories = [
  "Any Weather",
  "Cold ❄️ -10-9ºC",
  "Cool ☁️ 10-15ºC ",
  "Warm ⛅ 16-24ºC",
  "Hot ☀️ 25-30ºC",
  "Very Hot 🔥 31ºC+",
];

const places = [
  {
    name: "London Heathrow",
    country: "United Kingdom",
    type: "airport",
    id: "LHR",
  },
  {
    name: "Eiffel Tower",
    country: "France",
    type: "landmark",
    id: "EFT",
  },
  {
    name: "Dubai International Airport",
    country: "UAE",
    type: "airport",
    id: "DXB",
  },
  {
    name: "Sydney Opera House",
    country: "Australia",
    type: "landmark",
    id: "SOH",
  },
  {
    name: "Los Angeles International Airport",
    country: "America",
    type: "airport",
    id: "LAX",
  },
  {
    name: "Statue of Liberty",
    country: "America",
    type: "landmark",
    id: "SOL",
  },
  {
    name: "Haneda Airport",
    country: "Japan",
    type: "airport",
    id: "HND",
  },
  {
    name: "Mount Fuji",
    country: "Japan",
    type: "landmark",
    id: "MFJ",
  },
];
const origins: Place[] = [
  {
    id: "JFK",
    name: "John F. Kennedy International Airport",
    country: "America",
  },
  { id: "LHR", name: "Heathrow Airport", country: "United Kingdom" },
  { id: "HND", name: "Haneda Airport", country: "Japan" },
  {
    id: "SFO",
    name: "San Francisco International Airport",
    country: "America",
  },
  { id: "DXB", name: "Dubai International Airport", country: "UAE" },
  {
    id: "LAX",
    name: "Los Angeles International Airport",
    country: "America",
  },
  { id: "ORD", name: "O'Hare International Airport", country: "America" },
  {
    id: "ATL",
    name: "Hartsfield-Jackson Atlanta International Airport",
    country: "America",
  },
];

const amentitiesIconMap = {
  beach: "/icons/amenities/beach.svg",
  spa: "/icons/amenities/spa.svg",
  pool: "/icons/amenities/pool.svg",
  gym: "/icons/amenities/gym.svg",
  tick: "/icons/amenities/tick.svg",
};
export { weatherCategories, places, origins, amentitiesIconMap };
