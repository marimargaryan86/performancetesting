<script lang="ts">
  import type { SearchResultsData } from "../../../../routes/search/[searchType=search_type]/+page.svelte";
  import SearchResultTile from "../../../../components/search-result-tile.svelte";

  export let searchResultsData: SearchResultsData = false;
</script>

<div class="page">
  <div class="filter-sidebar">
    <pre>
    {JSON.stringify(searchResultsData, null, 2)}
  </pre>
  </div>
  <div class="main-content">
    <div class="search-results">
      <SearchResultTile />
    </div>
  </div>
</div>

<style>
  .page {
    display: flex;
    margin-top: 250px;
  }

  .filter-sidebar {
    width: 450px;
  }

  .main-content {
    flex-grow: 1;
  }
</style>
