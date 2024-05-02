<script lang="ts">
  import type { SearchResultsData } from "../../../../routes/search/[searchType=search_type]/[origin]/[destination]/+page.svelte";
  import SearchHeader from "$lib/features/search/search-header.svelte";

  export let searchResultsData: SearchResultsData = false;
</script>

<div class="wrapper">
  <SearchHeader />

  <main>
    <div class="filters">
      <h2>Hello filters.</h2>
    </div>

    <div class="search-results">
      <h2>Hello hotels.</h2>
      <pre>{JSON.stringify(searchResultsData, null, 4)}</pre>
    </div>
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
    border: 1px dashed red;
    width: 100%;
    max-width: 1012px;
  }
</style>
