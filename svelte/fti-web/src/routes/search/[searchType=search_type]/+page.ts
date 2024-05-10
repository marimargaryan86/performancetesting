import { getSearchTypeFromURL, type SearchType } from "../../../params/search_type.js";

/** @type {import('../$types.js').PageServerLoad} */
export function load({ url }): { searchParamsObj: Record<string, string>; searchType: SearchType } {
  const queryParams = url.searchParams;
  const searchParams = Array.from(queryParams.entries());
  const searchParamsObj = Object.fromEntries(searchParams);
  const searchType = getSearchTypeFromURL(url);

  return { searchParamsObj, searchType };
}
