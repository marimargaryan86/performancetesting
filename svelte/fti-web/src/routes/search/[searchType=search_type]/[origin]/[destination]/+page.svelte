<script lang="ts" context="module">
  export type SearchResultsData =
    | boolean
    | {
        test: boolean;
        data: Array<unknown>;
      };
</script>

<script lang="ts">
  import { browser } from "$app/environment";
  import LoadingScreen from "$lib/components/loading-screen.svelte";
  import HotelSearch from "$lib/features/search/hotels/hotel-search.svelte";
  import SearchStub from "$lib/features/search/search-stub.svelte";
  import type { SearchType } from "../../../../../params/search_type";

  export let data;
  let searchType: SearchType;

  function fetchSearchResults(): Promise<{ test: boolean; data: Array<unknown> }> | boolean {
    // temp mock, Sandeep request
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ test: true, data: [{}] });
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
