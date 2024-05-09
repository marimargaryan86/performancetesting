/* eslint-disable max-lines-per-function */
import accomodations, { type Accommodation } from "$lib/data/accommodations";
import { createSlug } from "$lib/helpers/common";
import { availablePackages } from "./available-packages";
import destinations from "./destinations";

interface FlightDetails {
  time: string;
  airport: string;
  duration: string;
  stops: number;
  direct: boolean;
  arrivalTime: string;
  arrivalAirport: string;
}

interface SelectedDate {
  start: string;
  end: string;
}

interface FlightSummary {
  date: string;
  duration: string;
  flightNumber: string;
  stops: string;
  departureTime: string;
  departureAirport: string;
  arrivalTime: string;
  arrivalAirport: string;
}

export interface Package {
  id: string;
  name: string;
  slug: string;
  stars: number;
  price: number;
  length: string;
  description: string;
  image: string;
  accommodations: Accommodation[];
  flights: {
    outbound: FlightDetails;
    inbound: FlightDetails;
  };
  selectedDates: SelectedDate;
  flightSummaries: {
    outbound: FlightSummary;
    inbound: FlightSummary;
  };
}

export const packageMap: Record<string, Package> = {};

function getLowestPrice(ac: Accommodation[]): number {
  return Math.min(
    ...ac.map(
      (a) =>
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        a.accommodationDetails.find((detail) => detail.roomType === a.hotel.roomTypes[0])!
          .pricePerDay,
    ),
  );
}

const packages: Package[] = destinations
  .filter((dest) => availablePackages.includes(dest.slug))
  .map((dest) => {
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const accs = accomodations.filter((a) => a.hotel.city === dest.name)!;
    const pkg: Package = {
      id: dest.id,
      name: `${accs[0].hotel.city}, ${accs[0].hotel.country}`,
      slug: createSlug(dest.name),
      price: getLowestPrice(accs),
      stars: 5,
      length: "10 days",
      description: "10 nights, all inclusive, flights included",
      image: `/images/destinations/${dest.id}.jpg`,
      accommodations: accs,
      flights: {
        outbound: {
          time: "08:25",
          airport: "LHR",
          duration: "17h 35m",
          stops: 2,
          direct: false,
          arrivalTime: "10:05",
          arrivalAirport: "DPS",
        },
        inbound: {
          time: "17:20",
          airport: "DPS",
          duration: "17h 35m",
          stops: 0,
          direct: true,
          arrivalTime: "03:55",
          arrivalAirport: "LHR",
        },
      },
      selectedDates: {
        start: "02/08/24",
        end: "12/08/24",
      },
      flightSummaries: {
        outbound: {
          date: "Tue, 2 Apr 2024",
          duration: "17h 40m",
          flightNumber: "SA941",
          stops: "2 stops",
          departureTime: "10:25",
          departureAirport: "London Heathrow, T2",
          arrivalTime: "12:05",
          arrivalAirport: "Bali Denpasar, T1",
        },
        inbound: {
          date: "Fri, 12 Apr 2024",
          duration: "17h 30m",
          flightNumber: "MH132",
          stops: "2 stops",
          departureTime: "19:20",
          departureAirport: "Bali Denpasar, T1",
          arrivalTime: "05:55",
          arrivalAirport: "London Heathrow, T5",
        },
      },
    };
    packageMap[dest.slug] = pkg;
    return pkg;
  });

export default packages;
