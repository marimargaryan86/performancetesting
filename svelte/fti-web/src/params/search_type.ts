/**
 * Contains route parameters for various search types. This lets us share
 * layouts and pages across the app.
 *
 */
export type SearchType = "hotels" | "flights" | "combo";

export function match(param: string): boolean {
  return param === "hotels" || param === "flights" || param === "combo";
}
