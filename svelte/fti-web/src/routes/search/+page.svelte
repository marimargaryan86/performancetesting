<script lang="ts">
  import { browser } from "$app/environment";
  import LoadingScreen from "$lib/components/loading-screen.svelte";
  import SearchResultTile from "../../components/search-result-tile.svelte";

  function fetchSearchResults(): Promise<{ test: boolean; data: Array<unknown> }> | boolean {
    // temp mock, Sandeep request
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ test: true, data: [{}] });
      }, 5000);
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
  {/await}
{:else}
  <LoadingScreen />
{/if}

<style>
  .page {
    display: flex;
    margin-top: 250px;
  }

  .filter-sidebar {
    width: 450px;
    background-color: #f5f5f5;
  }

  .main-content {
    flex-grow: 1;
  }
</style>
