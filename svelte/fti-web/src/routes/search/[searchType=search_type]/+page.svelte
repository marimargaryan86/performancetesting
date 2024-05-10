<script lang="ts" context="module">
  export type SearchResultsData = {
    test: boolean;
    data: Array<unknown>;
    origin: string | undefined;
    destination: string | undefined;
    passengers: Passengers | undefined;
  };
</script>

<script lang="ts">
  import { browser } from "$app/environment";
  import LoadingScreen from "$lib/components/loading-screen.svelte";
  import type { Accommodation } from "$lib/data/accommodations";
  import { packageMap } from "$lib/data/packages";
  import HotelSearch from "$lib/features/search/hotels/hotel-search.svelte";
  import SearchStub from "$lib/features/search/search-stub.svelte";
  import type { Passengers } from "$lib/models/common";
  import type { SearchType } from "../../../params/search_type";

  export let data;
  let searchType: SearchType;
  $: searchType = data.searchType;

  /**
   * TODO(2024-05-08:a.santos): figure out default destination strategy
   */
  function getHotelSearchResults(): Accommodation[] {
    const searchInfo = packageMap[data.searchParamsObj?.destination || "bali"];

    return searchInfo.accommodations;
  }

  // TODO(2024-05-06/a.santos): figure out passenger strategy, cookie or param
  function fetchSearchResults(): Promise<SearchResultsData> | undefined {
    // temp mock, Sandeep request
    let mockData = new Array({});
    if (searchType === "hotels") {
      mockData = getHotelSearchResults();
    }

    return new Promise((resolve) => {
      setTimeout(() => {
        const testSearchResultsData: SearchResultsData = {
          test: true,
          data: mockData,
          origin: data.searchParamsObj?.origin,
          destination: data.searchParamsObj?.destination,
          passengers: { adults: 2, children: 1 },
        };

        resolve(testSearchResultsData);
      }, 2000);
    });
  }
</script>

<svelte:head>
  <title>Search Results</title>
</svelte:head>

{#if browser}
  {#await fetchSearchResults()}
    <LoadingScreen />
  {:then searchResultsData}
    {#if searchType === "hotels"}
      <HotelSearch {searchResultsData} />
    {:else}
      <SearchStub {searchResultsData} />
    {/if}
  {/await}
{:else}
  <LoadingScreen />
{/if}
