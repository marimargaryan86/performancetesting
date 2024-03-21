<script lang="ts">
  import SearchResultTile from "../../components/search-result-tile.svelte";
</script>

<svelte:head>
  <title>Search Results</title>
</svelte:head>

<div class="page">
  <div class="filter-sidebar">
    <p>test</p>
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
    background-color: #f5f5f5;
  }

  .main-content {
    flex-grow: 1;
  }
</style>
