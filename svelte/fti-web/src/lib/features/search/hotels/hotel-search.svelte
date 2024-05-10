<script lang="ts">
  import type { SearchResultsData } from "../../../../routes/search/[searchType=search_type]/+page.svelte";
  import SearchHeader from "$lib/features/search/search-header.svelte";
  import { getTranslator } from "$lib/i18n";
  import type { SearchType } from "../../../../params/search_type";
  import type { SearchOptions } from "$lib/models/common";
  import type { Accommodation } from "$lib/data/accommodations";
  import Container from "$lib/components/container.svelte";
  import SearchResultTile from "../search-result-tile.svelte";

  const t = getTranslator();

  const HOTEL_SEARCH_TYPE: SearchType = "hotels";

  export let searchResultsData: SearchResultsData | undefined = undefined;
  let destination: string;
  let searchOptions: SearchOptions;
  let hotelData: Accommodation[] = [];

  $: destination =
    searchResultsData && searchResultsData?.destination
      ? searchResultsData?.destination
      : "anywhere";

  $: passengers =
    searchResultsData && searchResultsData?.passengers
      ? searchResultsData?.passengers
      : { adults: 1, children: 0 };

  $: searchOptions = {
    origin: undefined,
    destination,
    searchType: HOTEL_SEARCH_TYPE,
    passengers,
  };

  $: if (searchResultsData?.data) {
    hotelData = searchResultsData.data as Accommodation[];
  }
</script>

<div class="wrapper">
  <SearchHeader {searchOptions} />

  <main>
    <aside class="filters">
      <h2>{$t("sentences.hello")} filters.</h2>
    </aside>

    <section class="search-results">
      <header>
        <h2>{`${hotelData.length.toString()} ${$t("sentences.hotelsFound")}`}</h2>
        <button>Sort By</button>
      </header>
      {#if hotelData.length}
        <article>
          {#each hotelData as accommodation}
            <Container>
              <SearchResultTile {accommodation} />
            </Container>
          {/each}
        </article>
      {:else}
        <h4>No Search Results</h4>
      {/if}
    </section>
  </main>
</div>

<style>
  .wrapper {
    background-color: var(--colours-background-grey);
    width: 100%;
    height: 100vh;
    margin: 0;
  }

  main {
    padding: 76px 68px 0 68px;
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 24px;
    min-height: 1100px;
  }

  h2 {
    margin-left: 12px;
  }

  .filters {
    border: 1px dashed red;
    width: 330px;
  }

  .search-results {
    width: 100%;
    max-width: 1012px;
  }

  .search-results header {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  :global(.search-results article > div) {
    margin-bottom: 24px;
  }
</style>
