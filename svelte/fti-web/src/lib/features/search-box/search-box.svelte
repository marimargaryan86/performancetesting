<script lang="ts">
  import SearchBoxHeader from "./search-box-header.svelte";
  import SearchBoxPackages from "./search-box-packages.svelte";
  import { getSearchOptionsCtx, setSearchOptionsCtx } from "$lib/stores/search-box.store";
  import type { SearchOptions } from "$lib/models/common";
  import SearchBoxFlights from "./search-box-flights.svelte";
  import SearchBoxHotels from "./search-box-hotels.svelte";

  let searchOptions: SearchOptions = {
    passengers: { adults: 1, children: 0 },
    searchType: "combo",
    origin: "",
    destination: "",
  };

  setSearchOptionsCtx(searchOptions);

  const _searchOptions = getSearchOptionsCtx();
</script>

<SearchBoxHeader bind:searchType={$_searchOptions.searchType} />

<div class="search-panel">
  {#if $_searchOptions.searchType === "combo"}
    <SearchBoxPackages />
  {:else if $_searchOptions.searchType === "flights"}
    <SearchBoxFlights />
  {:else if $_searchOptions.searchType === "hotels"}
    <SearchBoxHotels />
  {/if}
</div>

<style>
  .search-panel {
    display: flex;
    flex-direction: column;
    padding: 20px 25px 35px;
    background-color: #ffffff;
    border-radius: 0 10px 10px;
  }

  @media only screen and (width <= 720px) {
    :global(.dropdown) {
      z-index: 99;
    }

    .search-panel {
      position: relative;
      left: 20px;
      width: 79.1%;
      border-top-right-radius: 0;
    }
  }
</style>
