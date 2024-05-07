import type { SearchOptions } from "$lib/models/common";

/**
 * Constructs a query string from search options.
 *
 * @param {SearchOptions} searchOptions - The search options to encode.
 * @returns {string} - The constructed query string, which looks like:
 *  "
 *    destination=NYC
 *    &origin=LAX
 *    &searchType=flights
 *    &passengers.adults=2
 *    &passengers.children=1
 *    &dates.start=2021-01-01
 *    &dates.end=2021-01-07
 *  "
 *
 */
export function constructQueryString(searchOptions: SearchOptions): string {
  const params = new URLSearchParams();

  params.set("destination", searchOptions.destination);
  params.set("origin", searchOptions.origin);
  params.set("searchType", searchOptions.searchType);

  Object.entries(searchOptions.passengers).forEach(([key, value]) => {
    const sanitizedPassengers = encodeURIComponent(`passengers.${key}`);
    params.set(sanitizedPassengers, String(value));
  });

  searchOptions.rooms?.forEach((room, index) => {
    Object.entries(room).forEach(([key, value]) => {
      const sanitizedRooms = encodeURIComponent(`rooms.${index}.${key}`);
      params.set(sanitizedRooms, String(value));
    });
  });

  if (searchOptions.dates) {
    Object.entries(searchOptions.dates).forEach(([key, value]) => {
      const sanitizedDates = encodeURIComponent(`dates.${key}`);
      params.set(sanitizedDates, value);
    });
  }

  return params.toString();
}
