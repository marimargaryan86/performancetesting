import type { SearchOptions } from "$lib/models/common";
import { toTitleCase } from "./common";
// TODO(04-24-2024/a.santos): Implement i18n translatable strings.

/**
 * TODO(04-26-2024/a.santos): Get real support number.
 *
 */
export const DEFAULT_SUPPORT_TELEPHONE_NUMBER: string = "089-710 4514 62";

/**
 * Default search options used as a placeholder before real data is fetched.
 *
 * @type {SearchOptions}
 */
export const DEFAULT_SEARCH_OPTIONS: SearchOptions = {
  destination: "",
  origin: "",
  searchType: "hotels",
  passengers: { adults: 2, children: 1 },
  rooms: [
    { adults: 1, children: 1 },
    { adults: 1, children: 0 },
  ],
  dates: {
    start: "08/01/2024",
    end: "08/15/2024",
  },
};

/**
 * Formats the origin and destination into a human-readable string.
 * Returns 'Anywhere' if both are empty.
 *
 * @param {SearchOptions} searchOptions - The search options containing origin and destination.
 * @returns {string} Formatted origin and destination string.
 */
export function formatOriginDestination(
  searchOptions: SearchOptions,
  config: { useTitleCase?: boolean; replaceHyphensWithSpaces?: boolean } = {},
): string {
  const { destination, origin } = searchOptions;
  let nextDestination = config.replaceHyphensWithSpaces
    ? destination.replaceAll("-", " ")
    : destination;
  let nextOrigin = config.replaceHyphensWithSpaces && origin ? origin.replaceAll("-", " ") : origin;
  nextDestination = config.useTitleCase ? toTitleCase(nextDestination) : nextDestination;
  nextOrigin = config.useTitleCase && nextOrigin ? toTitleCase(nextOrigin) : nextOrigin;

  if (nextOrigin === undefined || nextOrigin === "") {
    return nextDestination;
  }

  return `${nextOrigin}-${nextDestination}`;
}

/**
 * Formats the start and end dates into a human-readable string.
 * Returns 'Anytime' if both dates are empty.
 *
 * @param {SearchOptions} searchOptions - The search options containing date information.
 * @returns {string} Formatted date string.
 */
export function formatDates(searchOptions: SearchOptions): string {
  const { start, end } = searchOptions.dates ?? { start: "", end: "" };

  if (start === "" && end === "") {
    return "Anytime";
  }

  return `${start}-${end}`;
}

/**
 * Formats the number of adults, children, and rooms into a human-readable string.
 * Assumes a default of one room if no rooms are specified.
 *
 * @param {SearchOptions} searchOptions - The search options containing passengers and rooms.
 * @returns {string} Formatted string of passengers and rooms.
 */
export function formatPassengersAndRooms(searchOptions: SearchOptions): string {
  const { passengers, rooms } = searchOptions;

  if (rooms === undefined) {
    throw new Error("Rooms undefined.");
  }

  const { adults, children } = passengers;

  const numAdults = adults + (adults === 1 ? " adult" : " adults");
  const numChildren = children + (children === 1 ? " child" : " children");
  const numRooms = rooms === undefined || rooms.length === 1 ? "1 room" : `${rooms.length} rooms`;

  let result = numAdults;
  if (children > 0) {
    result += `, ${numChildren}`;
  }
  result += `, ${numRooms}`;

  return result;
}
