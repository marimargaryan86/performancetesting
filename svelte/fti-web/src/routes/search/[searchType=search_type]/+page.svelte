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
  import HotelSearch from "$lib/features/search/hotels/hotel-search.svelte";
  import SearchStub from "$lib/features/search/search-stub.svelte";
  import type { Passengers } from "$lib/models/common";
  import type { SearchType } from "../../../params/search_type";

  export let data;
  let searchType: SearchType;

  // TODO(2024-05-06/a.santos): figure out passenger strategy, cookie or param
  function fetchSearchResults(): Promise<SearchResultsData> | undefined {
    // temp mock, Sandeep request
    return new Promise((resolve) => {
      setTimeout(() => {
        const testSearchResultsData: SearchResultsData = {
          test: true,
          data: new Array({}),
          origin: data.searchParamsObj?.origin,
          destination: data.searchParamsObj?.destination,
          passengers: { adults: 2, children: 1 },
        };

        resolve(testSearchResultsData);
      }, 2000);
    });
  }

  $: searchType = data.searchType;
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
