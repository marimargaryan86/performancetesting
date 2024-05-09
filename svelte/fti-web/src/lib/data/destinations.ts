import { createSlug } from "$lib/helpers/common";
import { availablePackages } from "./available-packages";
import type { Weather } from "./origins";

export interface Destination {
  id: string;
  name: string;
  slug: string;
  country: string;
  latitude: number;
  longitude: number;
  iataCode: string;
  image: string;
  averageWeather: Weather[];
  packageUrl?: string;
}

const destinations: Destination[] = [
  {
    name: "London",
    country: "United Kingdom",
    latitude: 51.5074,
    longitude: -0.1278,
    iataCode: "LHR",
    image: "london.jpg",
    averageWeather: [
      {
        temperature: 10,
        month: "January",
      },
      {
        temperature: 8,
        month: "February",
      },
      {
        temperature: 12,
        month: "March",
      },
      {
        temperature: 15,
        month: "April",
      },
      {
        temperature: 18,
        month: "May",
      },
      {
        temperature: 21,
        month: "June",
      },
      {
        temperature: 23,
        month: "July",
      },
      {
        temperature: 22,
        month: "August",
      },
      {
        temperature: 19,
        month: "September",
      },
      {
        temperature: 15,
        month: "October",
      },
      {
        temperature: 11,
        month: "November",
      },
      {
        temperature: 7,
        month: "December",
      },
    ],
    id: "a64a5011-f7ae-487d-a7e3-570423dc69e4",
  },
  {
    name: "Tokyo",
    country: "Japan",
    latitude: 35.6895,
    longitude: 139.6917,
    iataCode: "HND",
    image: "tokyo.jpg",
    averageWeather: [
      {
        temperature: 5,
        month: "January",
      },
      {
        temperature: 6,
        month: "February",
      },
      {
        temperature: 10,
        month: "March",
      },
      {
        temperature: 16,
        month: "April",
      },
      {
        temperature: 21,
        month: "May",
      },
      {
        temperature: 24,
        month: "June",
      },
      {
        temperature: 27,
        month: "July",
      },
      {
        temperature: 29,
        month: "August",
      },
      {
        temperature: 25,
        month: "September",
      },
      {
        temperature: 19,
        month: "October",
      },
      {
        temperature: 14,
        month: "November",
      },
      {
        temperature: 8,
        month: "December",
      },
    ],
    id: "9e9f58a5-8d5b-451d-b97b-fed7ed6961ba",
  },
  {
    name: "Sydney",
    country: "Australia",
    latitude: -33.8688,
    longitude: 151.2093,
    iataCode: "SYD",
    image: "sydney.jpg",
    averageWeather: [
      {
        temperature: 26,
        month: "January",
      },
      {
        temperature: 26,
        month: "February",
      },
      {
        temperature: 25,
        month: "March",
      },
      {
        temperature: 23,
        month: "April",
      },
      {
        temperature: 20,
        month: "May",
      },
      {
        temperature: 17,
        month: "June",
      },
      {
        temperature: 15,
        month: "July",
      },
      {
        temperature: 16,
        month: "August",
      },
      {
        temperature: 18,
        month: "September",
      },
      {
        temperature: 21,
        month: "October",
      },
      {
        temperature: 23,
        month: "November",
      },
      {
        temperature: 25,
        month: "December",
      },
    ],
    id: "4760f9e6-06c6-4746-82cd-97835f0caaeb",
  },
  {
    name: "Paris",
    country: "France",
    latitude: 48.8566,
    longitude: 2.3522,
    iataCode: "CDG",
    image: "paris.jpg",
    averageWeather: [
      {
        temperature: 3,
        month: "January",
      },
      {
        temperature: 4,
        month: "February",
      },
      {
        temperature: 8,
        month: "March",
      },
      {
        temperature: 12,
        month: "April",
      },
      {
        temperature: 16,
        month: "May",
      },
      {
        temperature: 20,
        month: "June",
      },
      {
        temperature: 22,
        month: "July",
      },
      {
        temperature: 22,
        month: "August",
      },
      {
        temperature: 19,
        month: "September",
      },
      {
        temperature: 14,
        month: "October",
      },
      {
        temperature: 9,
        month: "November",
      },
      {
        temperature: 5,
        month: "December",
      },
    ],
    id: "cb7c998f-1305-451b-8128-1651bfbb3426",
  },
  {
    name: "Rome",
    country: "Italy",
    latitude: 41.9028,
    longitude: 12.4964,
    iataCode: "FCO",
    image: "rome.jpg",
    averageWeather: [
      {
        temperature: 7,
        month: "January",
      },
      {
        temperature: 8,
        month: "February",
      },
      {
        temperature: 11,
        month: "March",
      },
      {
        temperature: 14,
        month: "April",
      },
      {
        temperature: 18,
        month: "May",
      },
      {
        temperature: 22,
        month: "June",
      },
      {
        temperature: 25,
        month: "July",
      },
      {
        temperature: 25,
        month: "August",
      },
      {
        temperature: 22,
        month: "September",
      },
      {
        temperature: 17,
        month: "October",
      },
      {
        temperature: 12,
        month: "November",
      },
      {
        temperature: 8,
        month: "December",
      },
    ],
    id: "636ce561-669b-440f-9ccd-bbcfc5cdee03",
  },
  {
    name: "Cairo",
    country: "Egypt",
    latitude: 30.0444,
    longitude: 31.2357,
    iataCode: "CAI",
    image: "cairo.jpg",
    averageWeather: [
      {
        temperature: 18,
        month: "January",
      },
      {
        temperature: 19,
        month: "February",
      },
      {
        temperature: 21,
        month: "March",
      },
      {
        temperature: 25,
        month: "April",
      },
      {
        temperature: 28,
        month: "May",
      },
      {
        temperature: 30,
        month: "June",
      },
      {
        temperature: 31,
        month: "July",
      },
      {
        temperature: 32,
        month: "August",
      },
      {
        temperature: 30,
        month: "September",
      },
      {
        temperature: 27,
        month: "October",
      },
      {
        temperature: 23,
        month: "November",
      },
      {
        temperature: 20,
        month: "December",
      },
    ],
    id: "558a8d6c-2257-4f44-9eb6-45d72ca30f78",
  },
  {
    name: "Mumbai",
    country: "India",
    latitude: 19.076,
    longitude: 72.8777,
    iataCode: "BOM",
    image: "mumbai.jpg",
    averageWeather: [
      {
        temperature: 24,
        month: "January",
      },
      {
        temperature: 25,
        month: "February",
      },
      {
        temperature: 27,
        month: "March",
      },
      {
        temperature: 29,
        month: "April",
      },
      {
        temperature: 30,
        month: "May",
      },
      {
        temperature: 29,
        month: "June",
      },
      {
        temperature: 28,
        month: "July",
      },
      {
        temperature: 28,
        month: "August",
      },
      {
        temperature: 28,
        month: "September",
      },
      {
        temperature: 29,
        month: "October",
      },
      {
        temperature: 28,
        month: "November",
      },
      {
        temperature: 25,
        month: "December",
      },
    ],
    id: "8856fb85-14e8-46b5-a422-f4dbf19c436d",
  },
  {
    name: "Berlin",
    country: "Germany",
    latitude: 52.52,
    longitude: 13.405,
    iataCode: "TXL",
    image: "berlin.jpg",
    averageWeather: [
      {
        temperature: 0,
        month: "January",
      },
      {
        temperature: 1,
        month: "February",
      },
      {
        temperature: 5,
        month: "March",
      },
      {
        temperature: 9,
        month: "April",
      },
      {
        temperature: 14,
        month: "May",
      },
      {
        temperature: 18,
        month: "June",
      },
      {
        temperature: 20,
        month: "July",
      },
      {
        temperature: 20,
        month: "August",
      },
      {
        temperature: 16,
        month: "September",
      },
      {
        temperature: 11,
        month: "October",
      },
      {
        temperature: 6,
        month: "November",
      },
      {
        temperature: 2,
        month: "December",
      },
    ],
    id: "d339bf01-436c-4241-855f-c6f7ac416c43",
  },
  {
    name: "Beijing",
    country: "China",
    latitude: 39.9042,
    longitude: 116.4074,
    iataCode: "PEK",
    image: "beijing.jpg",
    averageWeather: [
      {
        temperature: -3,
        month: "January",
      },
      {
        temperature: 0,
        month: "February",
      },
      {
        temperature: 7,
        month: "March",
      },
      {
        temperature: 15,
        month: "April",
      },
      {
        temperature: 21,
        month: "May",
      },
      {
        temperature: 26,
        month: "June",
      },
      {
        temperature: 28,
        month: "July",
      },
      {
        temperature: 27,
        month: "August",
      },
      {
        temperature: 22,
        month: "September",
      },
      {
        temperature: 15,
        month: "October",
      },
      {
        temperature: 7,
        month: "November",
      },
      {
        temperature: 0,
        month: "December",
      },
    ],
    id: "8817e065-8a3d-4847-9ae4-b07efc0aea65",
  },
  {
    name: "Rio de Janeiro",
    country: "Brazil",
    latitude: -22.9068,
    longitude: -43.1729,
    iataCode: "GIG",
    image: "rio.jpg",
    averageWeather: [
      {
        temperature: 27,
        month: "January",
      },
      {
        temperature: 27,
        month: "February",
      },
      {
        temperature: 27,
        month: "March",
      },
      {
        temperature: 25,
        month: "April",
      },
      {
        temperature: 24,
        month: "May",
      },
      {
        temperature: 22,
        month: "June",
      },
      {
        temperature: 22,
        month: "July",
      },
      {
        temperature: 23,
        month: "August",
      },
      {
        temperature: 24,
        month: "September",
      },
      {
        temperature: 25,
        month: "October",
      },
      {
        temperature: 26,
        month: "November",
      },
      {
        temperature: 27,
        month: "December",
      },
    ],
    id: "c8d62066-bb6a-469a-b229-89fac857ea5d",
  },
  {
    name: "Amsterdam",
    country: "Netherlands",
    latitude: 52.3676,
    longitude: 4.9041,
    iataCode: "AMS",
    image: "amsterdam.jpg",
    averageWeather: [
      {
        temperature: 3,
        month: "January",
      },
      {
        temperature: 3,
        month: "February",
      },
      {
        temperature: 6,
        month: "March",
      },
      {
        temperature: 9,
        month: "April",
      },
      {
        temperature: 13,
        month: "May",
      },
      {
        temperature: 16,
        month: "June",
      },
      {
        temperature: 18,
        month: "July",
      },
      {
        temperature: 18,
        month: "August",
      },
      {
        temperature: 15,
        month: "September",
      },
      {
        temperature: 11,
        month: "October",
      },
      {
        temperature: 7,
        month: "November",
      },
      {
        temperature: 4,
        month: "December",
      },
    ],
    id: "4dc78ec9-4b3d-4243-a0c8-089ecd4817fd",
  },
  {
    name: "Dubai",
    country: "United Arab Emirates",
    latitude: 25.276987,
    longitude: 55.296249,
    iataCode: "DXB",
    image: "dubai.jpg",
    averageWeather: [
      {
        temperature: 19,
        month: "January",
      },
      {
        temperature: 20,
        month: "February",
      },
      {
        temperature: 23,
        month: "March",
      },
      {
        temperature: 26,
        month: "April",
      },
      {
        temperature: 30,
        month: "May",
      },
      {
        temperature: 32,
        month: "June",
      },
      {
        temperature: 34,
        month: "July",
      },
      {
        temperature: 35,
        month: "August",
      },
      {
        temperature: 32,
        month: "September",
      },
      {
        temperature: 29,
        month: "October",
      },
      {
        temperature: 25,
        month: "November",
      },
      {
        temperature: 21,
        month: "December",
      },
    ],
    id: "034e7746-eeff-4fb9-a874-cc1ee0539319",
  },
  {
    name: "Bangkok",
    country: "Thailand",
    latitude: 13.7563,
    longitude: 100.5018,
    iataCode: "BKK",
    image: "bangkok.jpg",
    averageWeather: [
      {
        temperature: 27,
        month: "January",
      },
      {
        temperature: 28,
        month: "February",
      },
      {
        temperature: 29,
        month: "March",
      },
      {
        temperature: 30,
        month: "April",
      },
      {
        temperature: 30,
        month: "May",
      },
      {
        temperature: 30,
        month: "June",
      },
      {
        temperature: 29,
        month: "July",
      },
      {
        temperature: 29,
        month: "August",
      },
      {
        temperature: 29,
        month: "September",
      },
      {
        temperature: 29,
        month: "October",
      },
      {
        temperature: 29,
        month: "November",
      },
      {
        temperature: 28,
        month: "December",
      },
    ],
    id: "c31082df-b679-42e6-b68b-07da8b9609a4",
  },
  {
    name: "Hong Kong",
    country: "China",
    latitude: 22.3193,
    longitude: 114.1694,
    iataCode: "HKG",
    image: "hong_kong.jpg",
    averageWeather: [
      {
        temperature: 17,
        month: "January",
      },
      {
        temperature: 17,
        month: "February",
      },
      {
        temperature: 19,
        month: "March",
      },
      {
        temperature: 23,
        month: "April",
      },
      {
        temperature: 26,
        month: "May",
      },
      {
        temperature: 28,
        month: "June",
      },
      {
        temperature: 29,
        month: "July",
      },
      {
        temperature: 29,
        month: "August",
      },
      {
        temperature: 28,
        month: "September",
      },
      {
        temperature: 26,
        month: "October",
      },
      {
        temperature: 23,
        month: "November",
      },
      {
        temperature: 19,
        month: "December",
      },
    ],
    id: "40279422-ddde-412e-92e1-e1beb753465d",
  },
  {
    name: "Singapore",
    country: "Singapore",
    latitude: 1.3521,
    longitude: 103.8198,
    iataCode: "SIN",
    image: "singapore.jpg",
    averageWeather: [
      {
        temperature: 27,
        month: "January",
      },
      {
        temperature: 27,
        month: "February",
      },
      {
        temperature: 28,
        month: "March",
      },
      {
        temperature: 28,
        month: "April",
      },
      {
        temperature: 28,
        month: "May",
      },
      {
        temperature: 28,
        month: "June",
      },
      {
        temperature: 27,
        month: "July",
      },
      {
        temperature: 27,
        month: "August",
      },
      {
        temperature: 27,
        month: "September",
      },
      {
        temperature: 27,
        month: "October",
      },
      {
        temperature: 27,
        month: "November",
      },
      {
        temperature: 27,
        month: "December",
      },
    ],
    id: "4beae98e-4bf6-48f1-8508-74e1874af704",
  },
  {
    name: "Seoul",
    country: "South Korea",
    latitude: 37.5665,
    longitude: 126.978,
    iataCode: "ICN",
    image: "seoul.jpg",
    averageWeather: [
      {
        temperature: -2,
        month: "January",
      },
      {
        temperature: 0,
        month: "February",
      },
      {
        temperature: 5,
        month: "March",
      },
      {
        temperature: 12,
        month: "April",
      },
      {
        temperature: 17,
        month: "May",
      },
      {
        temperature: 22,
        month: "June",
      },
      {
        temperature: 25,
        month: "July",
      },
      {
        temperature: 26,
        month: "August",
      },
      {
        temperature: 21,
        month: "September",
      },
      {
        temperature: 15,
        month: "October",
      },
      {
        temperature: 7,
        month: "November",
      },
      {
        temperature: 0,
        month: "December",
      },
    ],
    id: "475d5edb-046e-417b-8409-bd830bbd3f9d",
  },
  {
    name: "Moscow",
    country: "Russia",
    latitude: 55.7558,
    longitude: 37.6176,
    iataCode: "SVO",
    image: "moscow.jpg",
    averageWeather: [
      {
        temperature: -10,
        month: "January",
      },
      {
        temperature: -8,
        month: "February",
      },
      {
        temperature: -3,
        month: "March",
      },
      {
        temperature: 5,
        month: "April",
      },
      {
        temperature: 12,
        month: "May",
      },
      {
        temperature: 17,
        month: "June",
      },
      {
        temperature: 20,
        month: "July",
      },
      {
        temperature: 18,
        month: "August",
      },
      {
        temperature: 12,
        month: "September",
      },
      {
        temperature: 5,
        month: "October",
      },
      {
        temperature: -2,
        month: "November",
      },
      {
        temperature: -8,
        month: "December",
      },
    ],
    id: "697e89b7-faf2-42b7-ad50-ff7565367f24",
  },
  {
    name: "Toronto",
    country: "Canada",
    latitude: 43.65107,
    longitude: -79.347015,
    iataCode: "YYZ",
    image: "toronto.jpg",
    averageWeather: [
      {
        temperature: -3,
        month: "January",
      },
      {
        temperature: -3,
        month: "February",
      },
      {
        temperature: 1,
        month: "March",
      },
      {
        temperature: 8,
        month: "April",
      },
      {
        temperature: 14,
        month: "May",
      },
      {
        temperature: 19,
        month: "June",
      },
      {
        temperature: 22,
        month: "July",
      },
      {
        temperature: 22,
        month: "August",
      },
      {
        temperature: 18,
        month: "September",
      },
      {
        temperature: 12,
        month: "October",
      },
      {
        temperature: 6,
        month: "November",
      },
      {
        temperature: 0,
        month: "December",
      },
    ],
    id: "a90e9596-4ac1-419f-b142-62bb8ec8e317",
  },
  {
    name: "Los Angeles",
    country: "United States",
    latitude: 34.0522,
    longitude: -118.2437,
    iataCode: "LAX",
    image: "los_angeles.jpg",
    averageWeather: [
      {
        temperature: 14,
        month: "January",
      },
      {
        temperature: 14,
        month: "February",
      },
      {
        temperature: 15,
        month: "March",
      },
      {
        temperature: 16,
        month: "April",
      },
      {
        temperature: 18,
        month: "May",
      },
      {
        temperature: 20,
        month: "June",
      },
      {
        temperature: 23,
        month: "July",
      },
      {
        temperature: 24,
        month: "August",
      },
      {
        temperature: 23,
        month: "September",
      },
      {
        temperature: 21,
        month: "October",
      },
      {
        temperature: 18,
        month: "November",
      },
      {
        temperature: 14,
        month: "December",
      },
    ],
    id: "e71a9f1f-c6bb-460a-837e-e051b0cf8b3e",
  },
  {
    name: "New York City",
    country: "United States",
    latitude: 40.7128,
    longitude: -74.006,
    iataCode: "JFK",
    image: "nyc.jpg",
    averageWeather: [
      {
        temperature: -3,
        month: "January",
      },
      {
        temperature: -2,
        month: "February",
      },
      {
        temperature: 3,
        month: "March",
      },
      {
        temperature: 10,
        month: "April",
      },
      {
        temperature: 16,
        month: "May",
      },
      {
        temperature: 22,
        month: "June",
      },
      {
        temperature: 26,
        month: "July",
      },
      {
        temperature: 25,
        month: "August",
      },
      {
        temperature: 20,
        month: "September",
      },
      {
        temperature: 14,
        month: "October",
      },
      {
        temperature: 8,
        month: "November",
      },
      {
        temperature: 2,
        month: "December",
      },
    ],
    id: "673c5b55-eb6e-4c22-90b4-d442c22f4ee3",
  },
  {
    name: "Malaga",
    country: "Spain",
    latitude: 36.7213,
    longitude: -4.4213,
    iataCode: "AGP",
    image: "malaga.jpg",
    averageWeather: [
      {
        temperature: 11,
        month: "January",
      },
      {
        temperature: 12,
        month: "February",
      },
      {
        temperature: 14,
        month: "March",
      },
      {
        temperature: 16,
        month: "April",
      },
      {
        temperature: 19,
        month: "May",
      },
      {
        temperature: 23,
        month: "June",
      },
      {
        temperature: 26,
        month: "July",
      },
      {
        temperature: 26,
        month: "August",
      },
      {
        temperature: 24,
        month: "September",
      },
      {
        temperature: 20,
        month: "October",
      },
      {
        temperature: 16,
        month: "November",
      },
      {
        temperature: 13,
        month: "December",
      },
    ],
    id: "ee230911-fe14-43ea-8087-2612b1e50d59",
  },
  {
    name: "Lake Como",
    country: "Italy",
    latitude: 45.9865,
    longitude: 9.2742,
    iataCode: "BGY",
    image: "lake_como.jpg",
    averageWeather: [
      {
        temperature: 2,
        month: "January",
      },
      {
        temperature: 3,
        month: "February",
      },
      {
        temperature: 7,
        month: "March",
      },
      {
        temperature: 11,
        month: "April",
      },
      {
        temperature: 16,
        month: "May",
      },
      {
        temperature: 20,
        month: "June",
      },
      {
        temperature: 23,
        month: "July",
      },
      {
        temperature: 23,
        month: "August",
      },
      {
        temperature: 19,
        month: "September",
      },
      {
        temperature: 14,
        month: "October",
      },
      {
        temperature: 8,
        month: "November",
      },
      {
        temperature: 4,
        month: "December",
      },
    ],
    id: "c189eeb6-ddc1-42c9-9c66-9481f50cbada",
  },
  {
    name: "Istanbul",
    country: "Turkey",
    latitude: 41.0082,
    longitude: 28.9784,
    iataCode: "IST",
    image: "istanbul.jpg",
    averageWeather: [
      {
        temperature: 6,
        month: "January",
      },
      {
        temperature: 7,
        month: "February",
      },
      {
        temperature: 8,
        month: "March",
      },
      {
        temperature: 12,
        month: "April",
      },
      {
        temperature: 17,
        month: "May",
      },
      {
        temperature: 21,
        month: "June",
      },
      {
        temperature: 24,
        month: "July",
      },
      {
        temperature: 24,
        month: "August",
      },
      {
        temperature: 20,
        month: "September",
      },
      {
        temperature: 16,
        month: "October",
      },
      {
        temperature: 12,
        month: "November",
      },
      {
        temperature: 8,
        month: "December",
      },
    ],
    id: "09d191c2-d168-471b-a35d-a9419124d4ee",
  },
  {
    name: "Bali",
    country: "Indonesia",
    latitude: -8.4095,
    longitude: 115.1889,
    iataCode: "DPS",
    image: "bali.jpg",
    averageWeather: [
      {
        temperature: 26,
        month: "January",
      },
      {
        temperature: 26,
        month: "February",
      },
      {
        temperature: 26,
        month: "March",
      },
      {
        temperature: 26,
        month: "April",
      },
      {
        temperature: 27,
        month: "May",
      },
      {
        temperature: 27,
        month: "June",
      },
      {
        temperature: 26,
        month: "July",
      },
      {
        temperature: 26,
        month: "August",
      },
      {
        temperature: 27,
        month: "September",
      },
      {
        temperature: 28,
        month: "October",
      },
      {
        temperature: 28,
        month: "November",
      },
      {
        temperature: 27,
        month: "December",
      },
    ],
    id: "3a394443-cb16-4739-a89c-fc96361a9a9b",
  },
  {
    name: "Cape Town",
    country: "South Africa",
    latitude: -33.9249,
    longitude: 18.4241,
    iataCode: "CPT",
    image: "cape_town.jpg",
    averageWeather: [
      {
        temperature: 20,
        month: "January",
      },
      {
        temperature: 20,
        month: "February",
      },
      {
        temperature: 19,
        month: "March",
      },
      {
        temperature: 17,
        month: "April",
      },
      {
        temperature: 15,
        month: "May",
      },
      {
        temperature: 13,
        month: "June",
      },
      {
        temperature: 12,
        month: "July",
      },
      {
        temperature: 12,
        month: "August",
      },
      {
        temperature: 13,
        month: "September",
      },
      {
        temperature: 15,
        month: "October",
      },
      {
        temperature: 17,
        month: "November",
      },
      {
        temperature: 19,
        month: "December",
      },
    ],
    id: "9cd5ce19-fdee-4e2a-b212-b35f400a7349",
  },
  {
    name: "Barcelona",
    country: "Spain",
    latitude: 41.3851,
    longitude: 2.1734,
    iataCode: "BCN",
    image: "barcelona.jpg",
    averageWeather: [
      {
        temperature: 11,
        month: "January",
      },
      {
        temperature: 11,
        month: "February",
      },
      {
        temperature: 13,
        month: "March",
      },
      {
        temperature: 15,
        month: "April",
      },
      {
        temperature: 18,
        month: "May",
      },
      {
        temperature: 22,
        month: "June",
      },
      {
        temperature: 25,
        month: "July",
      },
      {
        temperature: 26,
        month: "August",
      },
      {
        temperature: 24,
        month: "September",
      },
      {
        temperature: 20,
        month: "October",
      },
      {
        temperature: 15,
        month: "November",
      },
      {
        temperature: 12,
        month: "December",
      },
    ],
    id: "0db41e14-197e-4102-8b1a-ab582382dea4",
  },
  {
    name: "Prague",
    country: "Czech Republic",
    latitude: 50.0755,
    longitude: 14.4378,
    iataCode: "PRG",
    image: "prague.jpg",
    averageWeather: [
      {
        temperature: -1,
        month: "January",
      },
      {
        temperature: 0,
        month: "February",
      },
      {
        temperature: 4,
        month: "March",
      },
      {
        temperature: 9,
        month: "April",
      },
      {
        temperature: 14,
        month: "May",
      },
      {
        temperature: 17,
        month: "June",
      },
      {
        temperature: 19,
        month: "July",
      },
      {
        temperature: 19,
        month: "August",
      },
      {
        temperature: 15,
        month: "September",
      },
      {
        temperature: 10,
        month: "October",
      },
      {
        temperature: 4,
        month: "November",
      },
      {
        temperature: 0,
        month: "December",
      },
    ],
    id: "1baf755c-5daa-482b-aa56-d734c3b7d5fc",
  },
  {
    name: "Kyoto",
    country: "Japan",
    latitude: 35.0116,
    longitude: 135.7681,
    iataCode: "KIX",
    image: "kyoto.jpg",
    averageWeather: [
      {
        temperature: 5,
        month: "January",
      },
      {
        temperature: 6,
        month: "February",
      },
      {
        temperature: 10,
        month: "March",
      },
      {
        temperature: 15,
        month: "April",
      },
      {
        temperature: 20,
        month: "May",
      },
      {
        temperature: 24,
        month: "June",
      },
      {
        temperature: 28,
        month: "July",
      },
      {
        temperature: 31,
        month: "August",
      },
      {
        temperature: 27,
        month: "September",
      },
      {
        temperature: 21,
        month: "October",
      },
      {
        temperature: 15,
        month: "November",
      },
      {
        temperature: 9,
        month: "December",
      },
    ],
    id: "709f41e1-5c69-4492-b535-f99ef661aebc",
  },
  {
    name: "Marrakech",
    country: "Morocco",
    latitude: 31.6295,
    longitude: -7.9811,
    iataCode: "RAK",
    image: "marrakech.jpg",
    averageWeather: [
      {
        temperature: 18,
        month: "January",
      },
      {
        temperature: 18,
        month: "February",
      },
      {
        temperature: 20,
        month: "March",
      },
      {
        temperature: 21,
        month: "April",
      },
      {
        temperature: 22,
        month: "May",
      },
      {
        temperature: 25,
        month: "June",
      },
      {
        temperature: 28,
        month: "July",
      },
      {
        temperature: 29,
        month: "August",
      },
      {
        temperature: 28,
        month: "September",
      },
      {
        temperature: 25,
        month: "October",
      },
      {
        temperature: 21,
        month: "November",
      },
      {
        temperature: 18,
        month: "December",
      },
    ],
    id: "335be43f-53bd-409e-98b4-666a1bb4c052",
  },
  {
    name: "Venice",
    country: "Italy",
    latitude: 45.4408,
    longitude: 12.3155,
    iataCode: "VCE",
    image: "venice.jpg",
    averageWeather: [
      {
        temperature: 3,
        month: "January",
      },
      {
        temperature: 4,
        month: "February",
      },
      {
        temperature: 8,
        month: "March",
      },
      {
        temperature: 12,
        month: "April",
      },
      {
        temperature: 17,
        month: "May",
      },
      {
        temperature: 21,
        month: "June",
      },
      {
        temperature: 24,
        month: "July",
      },
      {
        temperature: 24,
        month: "August",
      },
      {
        temperature: 20,
        month: "September",
      },
      {
        temperature: 15,
        month: "October",
      },
      {
        temperature: 9,
        month: "November",
      },
      {
        temperature: 4,
        month: "December",
      },
    ],
    id: "468da135-7033-4d89-a6dc-b862f5072c68",
  },
].map((dest) => {
  const slug = createSlug(dest.name);
  const packageUrl = availablePackages.includes(slug) ? `/packages/${slug}` : undefined;
  return {
    ...dest,
    slug: createSlug(dest.name),
    packageUrl,
  };
});

export default destinations;
