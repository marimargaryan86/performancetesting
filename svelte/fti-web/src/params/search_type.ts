/**
 * Contains route parameters for various search types. This lets us share
 * layouts and pages across the app.
 *
 */
export type SearchType = "hotels" | "packages" | "car-rentals";

export function match(param: string): boolean {
  return param === "hotels" || param === "packages" || param === "car-rentals";
}

/**
 * Extracts the searchType from the provided URL given a pathname of this form:
 * "/search/searchType/origin/destination/"
 *
 * @param url - The URL object from which to extract the searchType.
 * @returns The extracted searchType as a `SearchType`.
 */
export function getSearchTypeFromURL(url: URL): SearchType {
  const segments = url.pathname.split("/").filter(Boolean);

  if (segments.length < 2) {
    throw new Error("Invalid URL format for extracting search type.");
  }

  const searchType = segments[1];

  if (match(searchType)) {
    return searchType as SearchType;
  }

  throw new Error("Invalid search type.");
}
