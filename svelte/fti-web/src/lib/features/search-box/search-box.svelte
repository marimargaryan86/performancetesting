<script lang="ts">
  import SearchBoxHeader from "./search-box-header.svelte";
  import SearchBoxPackages from "./search-box-packages.svelte";
  import { getSearchOptionsCtx, setSearchOptionsCtx } from "$lib/stores/search-box.store";
  import type { SearchOptions } from "$lib/models/common";
  import SearchBoxFlights from "./search-box-flights.svelte";
  import SearchBoxHotels from "./search-box-hotels.svelte";

  let searchOptions: SearchOptions = {
    passengers: { adults: 1, children: 0 },
    searchType: "packages",
    origin: "",
    destination: "",
  };

  setSearchOptionsCtx(searchOptions);

  const _searchOptions = getSearchOptionsCtx();
</script>

<div class="search-box-container">
  <SearchBoxHeader bind:searchType={$_searchOptions.searchType} />

  <div class="search-panel">
    {#if $_searchOptions.searchType === "packages"}
      <SearchBoxPackages />
    {:else if $_searchOptions.searchType === "flights"}
      <SearchBoxFlights />
    {:else if $_searchOptions.searchType === "hotels"}
      <SearchBoxHotels />
    {/if}
    <button class="search-button">Search</button>
  </div>
</div>

<style>
  .search-box-container {
    padding: 150px 0 100px;
    background: url("/images/landing-background.jpeg") no-repeat center center;
  }

  .search-panel {
    display: flex;
    align-items: center;
    margin: 0 76px;
    padding: 20px 25px;
    background-color: #ffffff;
    border-radius: 0 0 10px 10px;
    border-top-right-radius: 8px;
  }

  .search-box-container :global(.search-section:last-of-type) {
    border-right: none;
  }

  .search-button {
    width: 12.5%;
    height: 50px;
    color: white;
    background: var(--colours-primary-orange, #ea7121);
    border: none;
    border-radius: 4px;
  }

  @media only screen and (width <= 720px) {
    :global(.dropdown) {
      z-index: 99;
    }

    .search-panel {
      flex-direction: column;
      margin: 0 20px;
      padding: 20px;
      border-top-right-radius: 0;
    }

    .search-button {
      width: 100%;
      margin-top: 20px;
    }
  }
</style>
