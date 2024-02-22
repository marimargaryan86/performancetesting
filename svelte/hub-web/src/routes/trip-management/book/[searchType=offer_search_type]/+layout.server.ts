import type { SearchType } from "~/params/offer_search_type";

export function load(event): { searchType: SearchType } {
  return { searchType: event.params.searchType };
}
