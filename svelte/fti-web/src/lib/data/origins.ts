import { createSlug } from "$lib/helpers/common";

export interface Weather {
  temperature: number;
  month: string;
}

export interface Origin {
  name: string;
  slug: string;
  latitude: number;
  longitude: number;
  iataCode: string;
  averageWeather: Weather[];
}

const origins: Origin[] = [
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
    id: "985e29b9-9514-4e2d-a4dc-160eddf39bbd",
  },
  {
    name: "Munich",
    country: "Germany",
    latitude: 48.1351,
    longitude: 11.582,
    iataCode: "MUC",
    image: "munich.jpg",
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
    id: "f7cbbb60-10c6-4c79-bcf4-1d12f3d33dc0",
  },
  {
    name: "Hamburg",
    country: "Germany",
    latitude: 53.5511,
    longitude: 9.9937,
    iataCode: "HAM",
    image: "hamburg.jpg",
    averageWeather: [
      {
        temperature: 1,
        month: "January",
      },
      {
        temperature: 1,
        month: "February",
      },
      {
        temperature: 4,
        month: "March",
      },
      {
        temperature: 8,
        month: "April",
      },
      {
        temperature: 12,
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
        temperature: 6,
        month: "November",
      },
      {
        temperature: 3,
        month: "December",
      },
    ],
    id: "5c1fc417-5017-4146-a47a-bb27b19fcbdf",
  },
  {
    name: "Cologne",
    country: "Germany",
    latitude: 50.9375,
    longitude: 6.9603,
    iataCode: "CGN",
    image: "cologne.jpg",
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
        temperature: 6,
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
        temperature: 11,
        month: "October",
      },
      {
        temperature: 6,
        month: "November",
      },
      {
        temperature: 3,
        month: "December",
      },
    ],
    id: "4ea4a2ac-5b51-4fda-8977-ae1deafd045e",
  },
  {
    name: "Frankfurt",
    country: "Germany",
    latitude: 50.1109,
    longitude: 8.6821,
    iataCode: "FRA",
    image: "frankfurt.jpg",
    averageWeather: [
      {
        temperature: 1,
        month: "January",
      },
      {
        temperature: 2,
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
    id: "d0f1a0ea-ac03-4c3b-8ec2-361388665065",
  },
  {
    name: "Vienna",
    country: "Austria",
    latitude: 48.2082,
    longitude: 16.3738,
    iataCode: "VIE",
    image: "vienna.jpg",
    averageWeather: [
      {
        temperature: 0,
        month: "January",
      },
      {
        temperature: 2,
        month: "February",
      },
      {
        temperature: 6,
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
        temperature: 13,
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
    id: "862dc5bb-d9bb-4278-a3d5-7d1d4198162c",
  },
  {
    name: "Salzburg",
    country: "Austria",
    latitude: 47.8095,
    longitude: 13.055,
    iataCode: "SZG",
    image: "salzburg.jpg",
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
    id: "db162972-75b7-4287-9415-92c2c92d4db0",
  },
  {
    name: "Innsbruck",
    country: "Austria",
    latitude: 47.2692,
    longitude: 11.4041,
    iataCode: "INN",
    image: "innsbruck.jpg",
    averageWeather: [
      {
        temperature: -3,
        month: "January",
      },
      {
        temperature: -1,
        month: "February",
      },
      {
        temperature: 3,
        month: "March",
      },
      {
        temperature: 8,
        month: "April",
      },
      {
        temperature: 13,
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
        temperature: 5,
        month: "November",
      },
      {
        temperature: -1,
        month: "December",
      },
    ],
    id: "3a7e7de3-55d0-4f5b-9337-78dbc4756970",
  },
  {
    name: "Graz",
    country: "Austria",
    latitude: 47.0707,
    longitude: 15.4395,
    iataCode: "GRZ",
    image: "graz.jpg",
    averageWeather: [
      {
        temperature: 0,
        month: "January",
      },
      {
        temperature: 2,
        month: "February",
      },
      {
        temperature: 6,
        month: "March",
      },
      {
        temperature: 10,
        month: "April",
      },
      {
        temperature: 15,
        month: "May",
      },
      {
        temperature: 19,
        month: "June",
      },
      {
        temperature: 21,
        month: "July",
      },
      {
        temperature: 21,
        month: "August",
      },
      {
        temperature: 17,
        month: "September",
      },
      {
        temperature: 12,
        month: "October",
      },
      {
        temperature: 5,
        month: "November",
      },
      {
        temperature: 1,
        month: "December",
      },
    ],
    id: "0fb37b43-8ad0-43ed-9e01-2b1ac14323c6",
  },
  {
    name: "Linz",
    country: "Austria",
    latitude: 48.3069,
    longitude: 14.2858,
    iataCode: "LNZ",
    image: "linz.jpg",
    averageWeather: [
      {
        temperature: 0,
        month: "January",
      },
      {
        temperature: 2,
        month: "February",
      },
      {
        temperature: 6,
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
        temperature: 19,
        month: "June",
      },
      {
        temperature: 21,
        month: "July",
      },
      {
        temperature: 21,
        month: "August",
      },
      {
        temperature: 17,
        month: "September",
      },
      {
        temperature: 12,
        month: "October",
      },
      {
        temperature: 5,
        month: "November",
      },
      {
        temperature: 1,
        month: "December",
      },
    ],
    id: "9ef87f8f-6ee0-44b4-b8ae-9be47c200ad9",
  },
].map((origin) => ({
  ...origin,
  slug: createSlug(origin.name),
}));

export default origins;
