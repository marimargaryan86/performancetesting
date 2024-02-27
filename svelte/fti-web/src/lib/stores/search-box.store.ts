import type { SearchOptions } from "$lib/models/common";
import { getContext, setContext } from "svelte";
import { writable, type Writable } from "svelte/store";

const SEARCH_OPTIONS_CTX = "searchOptions";

export function setSearchOptionsCtx(searchOptions: SearchOptions): Writable<SearchOptions> {
  return setContext(SEARCH_OPTIONS_CTX, writable(searchOptions));
}

export function getSearchOptionsCtx(): Writable<SearchOptions> {
  return getContext(SEARCH_OPTIONS_CTX);
}
